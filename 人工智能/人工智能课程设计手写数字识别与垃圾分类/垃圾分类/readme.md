## 1. 数据集
数据集下载地址：**https://ascend-professional-constructiondataset.obs.cn-north-4.myhuaweicloud.com:443/MindStudio-pc/data_en.zip**

## 2. 注意
我这里少了**ckpt_0**(模型的文件)，因为加载不上去，所以不加载

## 3. 预训练模型准备 
这个就是**mobilenetv2_cpu_gpu.ckpt**，下载地址**https://download.mindspore.cn/model_zoo/official/lite/mobilenetv2_openimage_lite/** ，下载后将其放置于以下目录： ./pretrain_checkpoint/

## 4. 脚本准备
在Gitee中克隆MindSpore开源项目仓库，进入./model_zoo/official/cv/mobilenetv2/直接下载。库的地址是**https://gitee.com/mindspore/mindspore**  
