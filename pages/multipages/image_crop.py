import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os


@st.cache_data(experimental_allow_widgets=True)  # 缓存加载数据
def input_string(label):
    '''
    :param label: string,‘输入保存文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**’
    :return: st.text_input
    '''
    return st.text_input(label)


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    '''
    :return: array, string
    '''
    # 设置上传选项
    uploaded_file = st.file_uploader('请选择一张图片上传', type=["jpg", "png"])
    # 返回图像和文件名
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img = np.asarray(image)
        file_name = uploaded_file.name
        return img, file_name
    else:
        return None, None


@st.cache_data(experimental_allow_widgets=True)
# 将图像按矩形框裁剪，自定义矩形框的位置
def crop_image(img):
    '''
    :param img: array
    :return: array
    '''
    st.subheader(":triangular_ruler: 裁剪原始图片")  # 📐
    col1, col2 = st.columns([50, 50])

    # 设定裁切的矩形框的左上角和右下角的坐标
    with col2:
        img_height, img_width, channels = img.shape
        x1 = st.slider("选择左上角的x坐标", 0, img_width - 1, 0)
        y1 = st.slider("选择左上角的y坐标", 0, img_height - 1, 0)
        x2 = st.slider("选择右下角的x坐标", x1 + 1, img_width, img_width)
        y2 = st.slider("选择右下角的y坐标", y1 + 1, img_height, img_height)
        cropped_img = img[y1:y2, x1:x2]

    # 显示原始图片和裁剪后的图片
    with col1:
        # 使用plt渲染图片，提前设置图形属性
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False
        # ---显示原始图片---
        fig1 = plt.figure()
        plt.title('原始图片')
        plt.imshow(img)

        plt.tight_layout()
        st.pyplot(fig1)

        # ---显示裁切后的图片---
        # 创建与原始图像相同大小的空白背景图像
        cropped_image = Image.fromarray(cropped_img)
        background = Image.new("RGB", (img_width, img_height), (255, 255, 255))
        # 将裁剪后的图像放置在原始图像的位置
        background.paste(cropped_image, (x1, y1))
        # 渲染图片
        fig2 = plt.figure()
        plt.title('裁切后的图片')
        plt.imshow(background)

        plt.tight_layout()
        st.pyplot(fig2)

    return cropped_img


@st.cache_data(experimental_allow_widgets=True)
# 将裁剪后的图像按网格线形式分块并保存
def block_img(img, file_name):
    '''
    :param img: array
    :param file_name: string
    :return:
    '''
    st.subheader(":triangular_ruler: 将裁剪后的图像按网格线形式分块")  # 📐
    col1, col2 = st.columns([50, 50])

    # 选择在裁剪后的矩形框中添加横线和竖线，自定义个数和移动位置
    with col1:
        num_hlines = st.number_input("选择横线的个数", min_value=0, max_value=10, value=0)
        num_vlines = st.number_input("选择竖线的个数", min_value=0, max_value=10, value=0)
        hline_positions = []
        vline_positions = []
        if num_hlines > 0:
            hline_positions = st.multiselect("**由上至下**选择横线的位置（百分比）", options=list(range(0, 101)), default=[50])
            if len(hline_positions) != num_hlines:
                st.warning(f"请确保选择{num_hlines}个位置")
        if num_vlines > 0:
            vline_positions = st.multiselect("**由左至右**选择竖线的位置（百分比）", options=list(range(0, 101)), default=[50])
            if len(vline_positions) != num_vlines:
                st.warning(f"请确保选择{num_vlines}个位置")

    # 显示网格后的图片
    with col2:
        height, width, channels = img.shape
        thickness = 3  # 网格线的厚度
        fig = plt.figure()
        plt.title('添加网格后的图片')
        plt.imshow(img)
        for p in hline_positions:
            y_percent = p / 100
            y = int(y_percent * height)
            plt.axhline(y=y, color='red', linewidth=3)  # 使用 Matplotlib 画横线
        for p in vline_positions:
            x_percent = p / 100
            x = int(x_percent * width)
            plt.axvline(x=x, color='red', linewidth=3)

        # 设置坐标刻度的标签为百分比
        plt.xticks(np.arange(0, 1.1, 0.1) * width, [f"{int(i * 10)}%" for i in range(11)])
        plt.yticks(np.arange(0, 1.1, 0.1) * height, [f"{int(i * 10)}%" for i in range(11)])
        plt.tight_layout()
        st.pyplot(fig)

    # ---计算分割后的子图像的坐标---
    hline_coords = [0] + [int(p / 100 * height) for p in hline_positions] + [height - 1]
    vline_coords = [0] + [int(p / 100 * width) for p in vline_positions] + [width - 1]
    sub_imgs = []
    for i in range(len(hline_coords) - 1):
        for j in range(len(vline_coords) - 1):
            sub_img = img[hline_coords[i] + thickness: hline_coords[i + 1] - thickness,
                        vline_coords[j] + thickness: vline_coords[j + 1] - thickness]
            sub_imgs.append(sub_img)

    # ---显示每一份子图像---
    fig = plt.figure()
    for i, sub_img in enumerate(sub_imgs):
        plt.subplot(len(hline_coords) - 1, len(vline_coords) - 1, i + 1)
        plt.title(f"子图像{i + 1}")
        plt.imshow(sub_img)
    plt.tight_layout()
    st.pyplot(fig)

    # ---保存每个子图像---
    # 设置子图像的名称
    img_names = []
    for i in range(len(sub_imgs)):
        name = st.text_input(f"请输入子图像{i + 1}的名称", value=f"{file_name[:-4]}({i + 1}).png")
        img_names.append(name)

    # 设置保存目录
    # save_dir = input_string("输入保存文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    save_dir = st.text_input("输入保存文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")

    # 设置一个保存图像的点击按钮
    if st.button("点击保存图像"):
        # 保存图像
        for i, sub_img in enumerate(sub_imgs):
            sub_image = Image.fromarray(sub_img)
            sub_image.save(os.path.join(save_dir, img_names[i]), quality=100)
        st.success("图像保存成功！")

    return None


def main():
    st.title(":scissors: 数据预处理——图片裁切工具")  # ✂️
    # 1.0 -----加载图片----
    img, origin_file_name = load_data()
    if img is not None:
        # 2.0 -----裁剪原始图片-----
        cropped_image = crop_image(img)
        # 3.0 -----将裁剪后的图像按网格线形式分块并保存-----
        block_img(cropped_image, origin_file_name)

    return None


if __name__ == "__main__":
    main()