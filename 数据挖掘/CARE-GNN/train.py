import torch
import torch.optim as optim
import numpy as np
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
import time
import argparse
from data_loader import DGraphDataset, BatchDataLoader
from care_gnn_model import CAREGNN, CAREGNNWithFocalLoss


def train_epoch(model, dataset, train_idx, optimizer, device, batch_size=1024, lambda_1=2.0):
    """训练一个epoch"""
    model.train()
    
    # 打乱训练数据
    np.random.shuffle(train_idx)
    
    total_loss = 0
    total_gnn_loss = 0
    total_label_loss = 0
    num_batches = (len(train_idx) + batch_size - 1) // batch_size
    
    for i in range(num_batches):
        start = i * batch_size
        end = min((i + 1) * batch_size, len(train_idx))
        batch_nodes = train_idx[start:end]
        batch_labels = dataset.labels[batch_nodes]

        # 确保标签是一维的
        if len(batch_labels.shape) > 1:
            batch_labels = batch_labels.squeeze()

        optimizer.zero_grad()

        # 计算损失
        loss, gnn_loss, label_loss = model.loss(
            batch_nodes,
            dataset.features,
            dataset.adj_lists,
            batch_labels,
            lambda_1=lambda_1
        )
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        total_gnn_loss += gnn_loss.item()
        total_label_loss += label_loss.item()
    
    avg_loss = total_loss / num_batches
    avg_gnn_loss = total_gnn_loss / num_batches
    avg_label_loss = total_label_loss / num_batches
    
    return avg_loss, avg_gnn_loss, avg_label_loss


def evaluate(model, dataset, eval_idx, device, batch_size=2048):
    """评估模型"""
    model.eval()

    all_probs = []
    all_labels = []

    num_batches = (len(eval_idx) + batch_size - 1) // batch_size

    with torch.no_grad():
        for i in range(num_batches):
            start = i * batch_size
            end = min((i + 1) * batch_size, len(eval_idx))
            batch_nodes = eval_idx[start:end]
            batch_labels = dataset.labels[batch_nodes]

            # 确保标签是一维的
            if len(batch_labels.shape) > 1:
                batch_labels = batch_labels.squeeze()

            probs = model.predict_proba(
                batch_nodes,
                dataset.features,
                dataset.adj_lists
            )

            all_probs.append(probs.cpu().numpy())
            all_labels.append(batch_labels.cpu().numpy())
    
    all_probs = np.vstack(all_probs)
    all_labels = np.concatenate(all_labels)

    # 预测类别
    pred_labels = np.argmax(all_probs, axis=1)

    # 计算指标
    accuracy = (pred_labels == all_labels).mean()

    # AUC (针对二分类)
    unique_labels = np.unique(all_labels)
    if len(unique_labels) >= 2:
        try:
            auc = roc_auc_score(all_labels, all_probs[:, 1])
        except ValueError as e:
            print(f"  Warning: AUC calculation failed: {e}")
            print(f"  Unique labels in eval set: {unique_labels}")
            print(f"  Pred prob stats - min: {all_probs[:, 1].min():.4f}, max: {all_probs[:, 1].max():.4f}, mean: {all_probs[:, 1].mean():.4f}")
            auc = 0.0
    else:
        print(f"  Warning: Only one class in eval set: {unique_labels}")
        auc = 0.0
    
    # 召回率 (Class 1)
    class1_mask = (all_labels == 1)
    if class1_mask.sum() > 0:
        recall = (pred_labels[class1_mask] == 1).mean()
    else:
        recall = 0.0
    
    # 精确率 (Class 1)
    pred_class1_mask = (pred_labels == 1)
    if pred_class1_mask.sum() > 0:
        precision = (all_labels[pred_class1_mask] == 1).mean()
    else:
        precision = 0.0
    
    # F1 分数
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0
    
    return {
        'accuracy': accuracy,
        'auc': auc,
        'recall': recall,
        'precision': precision,
        'f1': f1,
        'probs': all_probs
    }


def train_model(args):
    """主训练函数"""
    
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() and not args.no_cuda else 'cpu')
    print(f"Using device: {device}")
    
    # 加载数据
    print("\n" + "="*60)
    dataset = DGraphDataset(args.data_path)
    dataset.to_torch(device)
    
    # 获取训练数据
    train_idx, train_labels = dataset.get_train_data()
    
    # 处理类别不平衡 - 下采样
    if args.undersample > 1:
        class0_idx = train_idx[train_labels == 0]
        class1_idx = train_idx[train_labels == 1]
        
        # 下采样Class 0
        num_class0_keep = len(class1_idx) * args.undersample
        if num_class0_keep < len(class0_idx):
            class0_idx = np.random.choice(class0_idx, num_class0_keep, replace=False)
        
        train_idx = np.concatenate([class0_idx, class1_idx])
        train_labels = dataset.labels[train_idx].cpu().numpy()

        print(f"\nAfter undersampling - Class 0: {(train_labels == 0).sum()}, Class 1: {(train_labels == 1).sum()}")

    # 打乱数据再划分验证集（关键！确保验证集有两个类别）
    shuffle_idx = np.random.permutation(len(train_idx))
    train_idx = train_idx[shuffle_idx]

    # 创建验证集
    val_size = int(len(train_idx) * 0.2)
    val_idx = train_idx[:val_size]
    train_idx = train_idx[val_size:]

    # 验证两个集合都有两个类别
    val_labels = dataset.labels[val_idx].cpu().numpy()
    train_labels_check = dataset.labels[train_idx].cpu().numpy()
    print(f"\nVal set - Class 0: {(val_labels == 0).sum()}, Class 1: {(val_labels == 1).sum()}")
    print(f"Final train set - Class 0: {(train_labels_check == 0).sum()}, Class 1: {(train_labels_check == 1).sum()}")
    print(f"Final train size: {len(train_idx)}, Val size: {len(val_idx)}")
    
    # 创建模型
    print("\n" + "="*60)
    print("Creating CARE-GNN model...")
    
    if args.use_focal_loss:
        model = CAREGNNWithFocalLoss(
            feature_dim=dataset.num_features,
            embed_dim=args.embed_dim,
            num_relations=dataset.num_edge_types,
            num_classes=2,
            max_neighbors=args.max_neighbors,
            agg_type=args.agg_type,
            step_size=args.step_size,
            alpha=args.focal_alpha,
            gamma=args.focal_gamma,
            dataset=dataset,
            use_adaptive_sampling=args.use_adaptive_sampling,
            use_2hop=args.use_2hop
        ).to(device)
    else:
        model = CAREGNN(
            feature_dim=dataset.num_features,
            embed_dim=args.embed_dim,
            num_relations=dataset.num_edge_types,
            num_classes=2,
            max_neighbors=args.max_neighbors,
            agg_type=args.agg_type,
            step_size=args.step_size,
            dataset=dataset,
            use_adaptive_sampling=args.use_adaptive_sampling,
            use_2hop=args.use_2hop
        ).to(device)
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    if args.use_adaptive_sampling:
        print("  ✓ Adaptive sampling enabled")
    if args.use_2hop:
        print("  ✓ 2-hop neighbor expansion enabled")

    # 优化器
    optimizer = optim.Adam(
        model.parameters(),
        lr=args.lr,
        weight_decay=args.weight_decay
    )
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, 
        mode='max', 
        factor=0.5, 
        patience=5,
        verbose=True
    )
    
    # 训练循环
    print("\n" + "="*60)
    print("Starting training...")
    print("="*60)

    # 保存初始模型以防训练失败
    torch.save(model.state_dict(), 'best_model.pt')

    best_val_auc = 0
    best_epoch = 0
    patience_counter = 0
    
    for epoch in range(args.epochs):
        start_time = time.time()
        
        # 训练
        train_loss, train_gnn_loss, train_label_loss = train_epoch(
            model, dataset, train_idx, optimizer, device,
            batch_size=args.batch_size,
            lambda_1=args.lambda_1
        )
        
        # 验证
        if (epoch + 1) % args.eval_every == 0:
            val_metrics = evaluate(model, dataset, val_idx, device)
            
            epoch_time = time.time() - start_time

            print(f"\nEpoch {epoch+1}/{args.epochs} ({epoch_time:.2f}s)")
            print(f"  Train Loss: {train_loss:.4f} (GNN: {train_gnn_loss:.4f}, Label: {train_label_loss:.4f})")
            print(f"  Val Metrics:")
            print(f"    AUC: {val_metrics['auc']:.4f}")
            print(f"    Accuracy: {val_metrics['accuracy']:.4f}")
            print(f"    Recall: {val_metrics['recall']:.4f}")
            print(f"    Precision: {val_metrics['precision']:.4f}")
            print(f"    F1: {val_metrics['f1']:.4f}")

            # 添加预测分布统计
            probs = val_metrics['probs']
            pred_class1 = (probs[:, 1] > 0.5).sum()
            print(f"    Pred Class 1: {pred_class1}/{len(probs)} ({100*pred_class1/len(probs):.2f}%)")
            
            # 更新学习率

            scheduler.step(val_metrics['auc'])
            
            # 保存最佳模型
            if val_metrics['auc'] > best_val_auc:
                best_val_auc = val_metrics['auc']
                best_epoch = epoch + 1
                patience_counter = 0
                torch.save(model.state_dict(), 'best_model.pt')
                print(f"  *** Best model saved! ***")
            else:
                patience_counter += 1
            
            # 早停
            if patience_counter >= args.patience:
                print(f"\nEarly stopping at epoch {epoch+1}")
                break
    
    print("\n" + "="*60)
    print(f"Training completed!")
    print(f"Best validation AUC: {best_val_auc:.4f} at epoch {best_epoch}")
    print("="*60)

    # 加载最佳模型
    import os
    if os.path.exists('best_model.pt'):
        model.load_state_dict(torch.load('best_model.pt', weights_only=False))
        print("Loaded best model from best_model.pt")
    else:
        print("Warning: No best model found, using current model")
        # 保存当前模型作为最佳模型
        torch.save(model.state_dict(), 'best_model.pt')

    return model, dataset


def predict_test(model, dataset, device, output_path='submission.npy'):
    """对测试集进行预测"""
    print("\n" + "="*60)
    print("Predicting on test set...")
    
    test_idx = dataset.get_test_data()
    
    model.eval()
    all_probs = []
    
    batch_size = 2048
    num_batches = (len(test_idx) + batch_size - 1) // batch_size
    
    with torch.no_grad():
        for i in range(num_batches):
            start = i * batch_size
            end = min((i + 1) * batch_size, len(test_idx))
            batch_nodes = test_idx[start:end]
            
            probs = model.predict_proba(
                batch_nodes,
                dataset.features,
                dataset.adj_lists
            )
            
            all_probs.append(probs.cpu().numpy())
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i+1}/{num_batches} batches")
    
    all_probs = np.vstack(all_probs)
    
    # 保存结果 (只保留Class 1的概率)
    submission = all_probs[:, 1:2]  # Shape: (N, 1)
    
    # 转换为要求的格式 (N, 2) - [1-prob, prob]
    submission_full = np.hstack([1 - submission, submission])
    
    np.save(output_path, submission_full.astype(np.float32))
    print(f"Predictions saved to {output_path}")
    print(f"Submission shape: {submission_full.shape}")
    print("="*60)
    
    return submission_full


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CARE-GNN for DGraph')
    
    # 数据参数
    parser.add_argument('--data-path', type=str, default='phase1_gdata.npz',
                        help='Path to data file')
    
    # 模型参数
    parser.add_argument('--embed-dim', type=int, default=128,
                        help='Embedding dimension')
    parser.add_argument('--max-neighbors', type=int, default=30,
                        help='Maximum number of neighbors to sample')
    parser.add_argument('--agg-type', type=str, default='attention',
                        choices=['mean', 'attention', 'weight'],
                        help='Inter-relation aggregation type')
    parser.add_argument('--step-size', type=float, default=0.02,
                        help='RL step size for exploration')

    # 训练参数
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of epochs')
    parser.add_argument('--batch-size', type=int, default=512,
                        help='Batch size')
    parser.add_argument('--lr', type=float, default=0.0005,
                        help='Learning rate')
    parser.add_argument('--weight-decay', type=float, default=5e-5,
                        help='Weight decay')
    parser.add_argument('--lambda-1', type=float, default=1.5,
                        help='Label loss weight')
    parser.add_argument('--eval-every', type=int, default=1,
                        help='Evaluate every N epochs')
    parser.add_argument('--patience', type=int, default=20,
                        help='Early stopping patience')

    # 类别不平衡处理
    parser.add_argument('--undersample', type=int, default=8,
                        help='Undersampling ratio for majority class')
    parser.add_argument('--use-focal-loss', action='store_true', default=True,
                        help='Use Focal Loss instead of Cross Entropy')
    parser.add_argument('--focal-alpha', type=float, default=0.75,
                        help='Focal loss alpha parameter')
    parser.add_argument('--focal-gamma', type=float, default=3.0,
                        help='Focal loss gamma parameter')

    # 图采样优化参数
    parser.add_argument('--use-adaptive-sampling', action='store_true',
                        help='Use adaptive sampling based on node degree')
    parser.add_argument('--use-2hop', action='store_true',
                        help='Use 2-hop neighbors for low-degree nodes')
    
    # 其他参数
    parser.add_argument('--no-cuda', action='store_true',
                        help='Disable CUDA')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    parser.add_argument('--output', type=str, default='submission.npy',
                        help='Output file path')
    
    args = parser.parse_args()
    
    # 设置随机种子
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(args.seed)
    
    # 训练模型
    model, dataset = train_model(args)
    
    # 预测测试集
    device = torch.device('cuda' if torch.cuda.is_available() and not args.no_cuda else 'cpu')
    predictions = predict_test(model, dataset, device, args.output)
    
    print("\nDone!")
