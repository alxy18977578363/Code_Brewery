#!/usr/bin/env python
# coding: utf-8

# 水墨画风格Stable Diffusion微调完整代码

import os
import io
import torch
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
from dataclasses import dataclass
from tqdm.auto import tqdm
import glob
from torch.utils.data import DataLoader

# Hugging Face库
from transformers import CLIPTokenizer, CLIPTextModel
from diffusers import (
    StableDiffusionPipeline,
    UNet2DConditionModel,
    DDPMScheduler,
    get_cosine_schedule_with_warmup
)
from accelerate import Accelerator, notebook_launcher
from peft import LoraConfig, get_peft_model
import torch.nn.functional as F

# ======================
# 1. 配置类
# ======================

@dataclass
class TrainingConfig:
    # 模型配置
    pretrained_model = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    use_lora = True  # 使用LoRA进行高效微调
    
    # 数据配置
    dataset_path = "dataset.parquet"  # 您的诗词-水墨画数据集路径
    resolution = 512  # 图像分辨率
    
    # 训练参数
    train_batch_size = 2  # 根据GPU内存调整
    eval_batch_size = 2
    num_epochs = 50
    gradient_accumulation_steps = 1
    learning_rate = 1e-5
    lr_warmup_steps = 500
    mixed_precision = "fp16"  # 'no' for fp32, 'fp16' for mixed precision
    
    # 保存配置
    output_dir = "ink_wash_diffusion"
    save_image_steps = 500  # 每隔多少步保存示例图像
    save_model_steps = 2000  # 每隔多少步保存模型
    
    # 随机种子
    seed = 42

config = TrainingConfig()

# ======================
# 2. 数据集类
# ======================

class InkWashDataset(Dataset):
    def __init__(self, parquet_path, tokenizer, size=512):
        self.df = pd.read_parquet(parquet_path)
        self.tokenizer = tokenizer
        self.size = size
        self.transform = transforms.Compose([
            transforms.Resize(size),
            transforms.CenterCrop(size),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ])
        
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        # 获取图像
        img_dict = self.df.iloc[idx]["image"]
        image = Image.open(io.BytesIO(img_dict["bytes"]))
        image = self.transform(image.convert("RGB"))
        
        # 获取文本并添加风格前缀
        text = self.df.iloc[idx]["text"]
        prompt = f"中国传统水墨画风格，{text}"
        
        # 分词
        inputs = self.tokenizer(
            prompt,
            max_length=self.tokenizer.model_max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "pixel_values": image,
            "input_ids": inputs.input_ids[0],
            "attention_mask": inputs.attention_mask[0]
        }

# ======================
# 3. 辅助函数
# ======================

def generate_samples(pipeline, step, config):
    """生成示例图像并保存"""
    # 示例诗词
    test_prompts = [
        "中国传统水墨画风格，日往菲薇，月来扶疏",
        "中国传统水墨画风格，雷雨窈冥而未半，皦日笼光於绮寮",
        "中国传统水墨画风格，蕙风如薰，甘露如醴"
    ]
    
    images = []
    for prompt in test_prompts:
        image = pipeline(prompt, num_inference_steps=50).images[0]
        images.append(image)
    
    # 保存图像
    os.makedirs(f"{config.output_dir}/samples", exist_ok=True)
    for i, img in enumerate(images):
        img.save(f"{config.output_dir}/samples/step_{step}_sample_{i}.png")

def save_model(pipeline, unet, step, config):
    """保存模型检查点"""
    save_path = f"{config.output_dir}/checkpoint-{step}"
    pipeline.save_pretrained(save_path)
    
    # 如果使用LoRA，单独保存适配器
    if config.use_lora:
        unet.save_pretrained(f"{save_path}/unet_lora")

# ======================
# 4. 训练函数
# ======================

def train_loop(config):
    # 初始化组件
    tokenizer = CLIPTokenizer.from_pretrained(
        config.pretrained_model,
        subfolder="tokenizer"
    )
    text_encoder = CLIPTextModel.from_pretrained(
        config.pretrained_model,
        subfolder="text_encoder"
    )
    unet = UNet2DConditionModel.from_pretrained(
        config.pretrained_model,
        subfolder="unet"
    )
    noise_scheduler = DDPMScheduler.from_pretrained(
        config.pretrained_model,
        subfolder="scheduler"
    )

    # 使用LoRA进行高效微调
    if config.use_lora:
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["to_k", "to_q", "to_v", "proj_out"],
            lora_dropout=0.1,
            bias="none"
        )
        unet = get_peft_model(unet, lora_config)
        unet.print_trainable_parameters()

    # 冻结文本编码器
    text_encoder.requires_grad_(False)

    # 准备数据集
    train_dataset = InkWashDataset(config.dataset_path, tokenizer, config.resolution)
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=config.train_batch_size,
        shuffle=True
    )

    # 优化器和学习率调度
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=config.learning_rate
    )
    lr_scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=config.lr_warmup_steps,
        num_training_steps=len(train_dataloader) * config.num_epochs
    )

    # 初始化accelerator
    accelerator = Accelerator(
        mixed_precision=config.mixed_precision,
        gradient_accumulation_steps=config.gradient_accumulation_steps
    )
    accelerator.init_trackers("ink_wash_training")

    # 准备组件
    unet, optimizer, train_dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, train_dataloader, lr_scheduler
    )

    # 创建保存目录
    os.makedirs(config.output_dir, exist_ok=True)

    # 训练循环
    global_step = 0
    progress_bar = tqdm(range(config.num_epochs * len(train_dataloader)))

    for epoch in range(config.num_epochs):
        unet.train()
        
        for batch in train_dataloader:
            with accelerator.accumulate(unet):
                # 准备数据
                latents = batch["pixel_values"] * 0.18215  # 近似VAE缩放因子
                noise = torch.randn_like(latents)
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps,
                    (latents.shape[0],),
                    device=latents.device
                ).long()
                
                # 添加噪声
                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)
                
                # 获取文本嵌入
                encoder_hidden_states = text_encoder(
                    batch["input_ids"],
                    attention_mask=batch["attention_mask"]
                )[0]
                
                # 预测噪声
                noise_pred = unet(
                    noisy_latents,
                    timesteps,
                    encoder_hidden_states=encoder_hidden_states
                ).sample
                
                # 计算损失
                loss = F.mse_loss(noise_pred, noise)
                accelerator.backward(loss)
                
                # 更新参数
                if accelerator.sync_gradients:
                    accelerator.clip_grad_norm_(unet.parameters(), 1.0)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()
            
            # 记录日志
            global_step += 1
            logs = {
                "loss": loss.detach().item(),
                "lr": lr_scheduler.get_last_lr()[0],
                "step": global_step
            }
            progress_bar.set_postfix(**logs)
            progress_bar.update(1)
            accelerator.log(logs, step=global_step)
            
            # 定期保存模型和生成示例
            if accelerator.is_main_process:
                if global_step % config.save_image_steps == 0:
                    # 创建临时pipeline用于生成示例
                    pipeline = StableDiffusionPipeline(
                        text_encoder=text_encoder,
                        tokenizer=tokenizer,
                        unet=accelerator.unwrap_model(unet),
                        scheduler=noise_scheduler,
                        safety_checker=None,
                        requires_safety_checker=False
                    ).to(accelerator.device)
                    generate_samples(pipeline, global_step, config)
                    del pipeline
                
                if global_step % config.save_model_steps == 0:
                    # 创建临时pipeline用于保存
                    pipeline = StableDiffusionPipeline(
                        text_encoder=text_encoder,
                        tokenizer=tokenizer,
                        unet=accelerator.unwrap_model(unet),
                        scheduler=noise_scheduler
                    )
                    save_model(pipeline, accelerator.unwrap_model(unet), global_step, config)
                    del pipeline

# ======================
# 5. 启动训练
# ======================

if __name__ == "__main__":
    # 启动训练
    args = (config,)
    notebook_launcher(train_loop, args, num_processes=1)

    # 训练完成后加载模型示例
    print("训练完成！使用以下代码加载模型：")
    print(f"""
    from diffusers import StableDiffusionPipeline
    import torch

    model_path = "{config.output_dir}/checkpoint-final"  # 替换为您的最终检查点
    pipe = StableDiffusionPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
    ).to("cuda")

    # 生成图像
    prompt = "中国传统水墨画风格，大漠孤烟直，长河落日圆"
    image = pipe(prompt, num_inference_steps=50).images[0]
    image.save("generated_poem.png")
    """)