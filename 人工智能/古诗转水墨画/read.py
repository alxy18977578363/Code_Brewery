import pandas as pd

# 读取 Parquet 文件
df = pd.read_parquet("dataset.parquet")

# 查看前几行数据
print(df.head())

from PIL import Image
import io


# 提取第一行的图像数据（字典格式）
image_dict = df.iloc[11]["image"]  # 示例: {'bytes': b'\xff\xd8\xff\xe0...'}

# 从字典中获取二进制数据并解码为图像
image_bytes = image_dict["bytes"]  # 提取键 "bytes" 对应的值
image = Image.open(io.BytesIO(image_bytes))


import matplotlib.pyplot as plt
from PIL import Image

img = Image.open(io.BytesIO(image_dict["bytes"]))
plt.imshow(img)
plt.axis("off")  # 隐藏坐标轴
plt.show()  # 显示图像