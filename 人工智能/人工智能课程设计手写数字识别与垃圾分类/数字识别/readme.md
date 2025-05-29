## 1. 环境安装
在 **https://www.mindspore.cn/** 的最后面有个 "快速安装",pip 即可
## 2. 数据集
```python
# Download data from open datasets
from download import download

url = "https://mindspore-website.obs.cn-north-4.myhuaweicloud.com/" \
      "notebook/datasets/MNIST_Data.zip"
path = download(url, "./", kind="zip", replace=True)
```
