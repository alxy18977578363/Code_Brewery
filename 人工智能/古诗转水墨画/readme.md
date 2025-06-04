# 古诗转水墨画（大模型）实验指南

## 实验内容
利用Stable Diffusion等深度学习技术，实现根据古诗自动生成水墨画的功能。学习Python编程语言在深度学习中的应用，掌握基于PyTorch的深度学习框架，了解可控生成大模型的原理与关键技术。

## 实验要求
1. **提供资源**  
   - Stable Diffusion大模型代码与预测参数  
   - 训练和测试数据集  
2. **任务**  
   - 自行部署Stable Diffusion模型  
   - 完成训练与调参  

## 选做内容
1. 训练模型生成写实画作  
2. 分析模型效果并提出改进方案  
3. 尝试其他可控生成模型  

## 实验环境
- **框架**：PyTorch  
- **辅助工具**：Pandas、Numpy、Sklearn（需注意版本匹配）  

## 硬件需求
- NVIDIA显卡（显存>22G，如RTX 3090/4090）  

---

## 数据集（任选其一）
1. **图片+标签**  
   - 格式：CSV文件（图片名 + 标签）  
   - 下载链接：[Paint4Poem-Web-famous-subset.zip](https://yunpan.tongji.edu.cn/link/AACE739FD0079847BC82BE6BB2FE453160)  

2. **HuggingFace Parquet数据集**  
   - 二进制封装，需通过`io`库读取  
   - 下载链接：[dataset.parquet](https://yunpan.tongji.edu.cn/link/AA8DCF7C32B2924A81B83144503AE5639D)  

---

## 预训练模型
- 下载链接：[stable-diffusion-v1-5.zip](https://yunpan.tongji.edu.cn/link/AAADD470591CCEA4E77A952DCCBA222CCAC)  

---

## 参考资料
- **Python教程**：[runoob.com](https://www.runoob.com/python3/python3-tutorial.html)  
- **Numpy**：[numpy.org](https://www.numpy.org)  
- **Sklearn**：[scikit-learn.org](https://scikit-learn.org)  
- **PyTorch**：[pytorch.org](https://pytorch.org/)  
- **文献**：*High-Resolution Image Synthesis with Latent Diffusion Models*  
- **HuggingFace模型**：[stable-diffusion-v1-5](https://huggingface.co/stable-diffusion-v1-5)  
- **Diffusers库**：[GitHub](https://github.com/huggingface/diffusers)  
