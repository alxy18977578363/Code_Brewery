import os
import cv2
import numpy as np


def cartoonize_image(img, ds_factor=4):
    # Convert image to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply median filter to the grayscale image
    img_gray = cv2.medianBlur(img_gray, 7)
    # Detect edges in the image and threshold it
    edges = cv2.Laplacian(img_gray, cv2.CV_8U, ksize=5)
    ret, mask = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY_INV)

    # Resize the image to a smaller size for faster computation
    img_small = cv2.resize(img, None, fx=1.0 / ds_factor, fy=1.0 / ds_factor, interpolation=cv2.INTER_AREA)
    num_repetitions = 10
    sigma_color = 5
    sigma_space = 7
    size = 5

    # Apply bilateral filter to the image multiple times
    for i in range(num_repetitions):
        img_small = cv2.bilateralFilter(img_small, size, sigma_color, sigma_space)

    img_output = cv2.resize(img_small, None, fx=ds_factor, fy=ds_factor, interpolation=cv2.INTER_LINEAR)

    # Convert img_output and mask to uint8
    img_output = img_output.astype(np.uint8)
    mask = mask.astype(np.uint8)

    # Ensure mask and img_output have the same size
    mask = cv2.resize(mask, (img_output.shape[1], img_output.shape[0]))

    # Create the final cartoonized image
    dst = cv2.bitwise_and(img_output, img_output, mask=mask)

    # Convert the cartoon image to grayscale (black and white)
    dst_gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

    return dst_gray
def main():
    # 获取当前目录
    current_dir = os.getcwd()

    # 指定输入和输出图像文件名
    input_image_filename = "2351136.jpg"  # 替换为你的输入图片文件名
    output_image_filename = "2351136carton.jpg"  # 替换为你的输出图片文件名

    # 构建输入和输出图像的完整路径（使用Unicode字符串）
    input_image_path = os.path.join(current_dir, input_image_filename)
    output_image_path = os.path.join(current_dir, output_image_filename)

    # 读取输入图像
    if not os.path.exists(input_image_path):
        print(f"输入图像 '{input_image_path}' 不存在.")
        return

    img = cv2.imread(input_image_path)

    # 生成卡通化图像
    img_cartoon = cartoonize_image(img)

    # 保存灰度卡通化图像
    cv2.imwrite(output_image_path, img_cartoon)
    print(f"卡通化图像已保存为 {output_image_path}")


if __name__ == "__main__":
    main()
