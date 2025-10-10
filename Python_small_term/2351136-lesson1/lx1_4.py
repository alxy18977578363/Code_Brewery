import qrcode

# 生成一个二维码
def qrgeneration():
    data = 'https://www.tongji.edu.cn/'
    img=qrcode.make(data)
    img.save("picture.png")

#测试程序
if __name__=="__main__":
    qrgeneration()


