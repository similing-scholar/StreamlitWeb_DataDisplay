import streamlit as st
from PIL import Image
import numpy as np
import streamlit_image_coordinates as sic
import matplotlib.pyplot as plt
import cv2
import os
import pandas as pd


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    '''
    :return: array
    '''
    uploaded_file = st.file_uploader('请选择一张图片上传', type=["jpg", "png"])
    # 返回图像和文件名
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img = np.asarray(image)
        file_name = uploaded_file.name
        return img, file_name
    else:
        return None, None


# 使用streamlit_image_coordinates库，渲染图片，并返回鼠标点击图像像素点的坐标
def get_img_coordinates(img):
    '''
    :param img: array
    :return:
    '''
    st.subheader(":point_down: 图像像素点位置获取面板")  # 👇
    value = sic.streamlit_image_coordinates(img, key="pil")
    if value is not None:
        point_x = value["x"]
        point_y = value["y"]
        st.write(f'点击上图获取的坐标位置为：{point_x}, {point_y}')
    else:
        st.write(':+1:请点击上方图片选择一个像素点')  # 👍
    return None


# 通过在图片上标记两个已知实际距离的像素点，计算出像素与实际距离的比例
@st.cache_data(experimental_allow_widgets=True)
def actual_size_mapping(img):
    '''
    :param img: array
    :return: float
    '''
    st.subheader(":straight_ruler: 计算图片像素距离与实际距离的映射比例")  # 📏
    col1, col2 = st.columns([40, 60])

    # ---坐标参数获取---
    with col1:
        # 添加输入框，用于传入第一个点击的坐标，默认值为图片三分之一处
        point1 = st.text_input('请输入第一个坐标点 x, y :', value=f'{img.shape[1] // 3}, {img.shape[0] // 3}')
        # 添加输入框，用于传入第二个点击的坐标，默认值为图片中心
        point2 = st.text_input('请输入第二个坐标点 x, y :', value=f'{img.shape[1] // 2}, {img.shape[0] // 2}')
        # 添加输入框，用于两个像素点的实际距离
        distance = st.text_input('请输入两个像素坐标间距映射的实际距离（单位为**毫米**）:', value=8)

        # 添加一些错误提示
        try:
            # 字符串分割并转换为整数值
            point1_x, point1_y = map(int, point1.split(','))
            point2_x, point2_y = map(int, point2.split(','))
            distance = float(distance)
        except ValueError:
            st.warning("请输入有效的坐标和距离值")

    # ---使用plt渲染原图，并标出两个点坐标，计算单位像素的实际距离---
    with col2:
        if point1 and point2 is not None:
            # 将输入的坐标点位置及周围像素的RGB值替换为黄色
            img_copy = img.copy()
            # 设置要替换像素点的半径
            radius = 1
            # 替换坐标点1及周围像素的RGB值，cv2.circle会直接对数组操作
            if 0 <= point1_x < img_copy.shape[1] and 0 <= point1_y < img_copy.shape[0]:
                cv2.circle(img_copy, (point1_x, point1_y), radius, [255, 255, 0], -1)
            if 0 <= point2_x < img_copy.shape[1] and 0 <= point2_y < img_copy.shape[0]:
                cv2.circle(img_copy, (point2_x, point2_y), radius, [255, 255, 0], -1)

            # 使用plt渲染图片，提前设置图形属性
            plt.rcParams['font.sans-serif'] = ['simhei']
            plt.rcParams['axes.unicode_minus'] = False

            fig = plt.figure()
            plt.title('添加了两个坐标点（黄色标识）的原始图片')
            plt.imshow(img_copy)  # 渲染修改后的copy图像
            plt.tight_layout()
            st.pyplot(fig)

            # 计算像素与实际距离的比例
            if point1_x != point2_x or point1_y != point2_y:
                pixel_distance = np.sqrt((point2_x - point1_x) ** 2 + (point2_y - point1_y) ** 2)
                scale = distance / pixel_distance
                # 居中对齐打印scale
                st.write(f'<center>像素与实际距离的比例为：{scale:.4f} 毫米/像素<center>', unsafe_allow_html=True)

                if scale is not None:
                    return scale


# 定义一个提取咖啡环图片颜色变化的类
class RadialProfileCalculator:
    #  定义一个函数，计算从圆心到新的圆，在指定方向上的灰度平均值随半径的变化
    def radial_profile_direction(self, img, center, new_radius, direction_angle_degrees):
        # 将方向角度转换为弧度
        direction_angle_radians = np.deg2rad(direction_angle_degrees)
        # 创建一个数组，存储每个半径对应的灰度平均值
        gray_values = []

        for i in range(new_radius + 1):
            # 计算当前点的坐标，从中心点开始，包括半径所在的一圈像素
            x = int(center[0] + i * np.cos(direction_angle_radians))
            y = int(center[1] + i * np.sin(direction_angle_radians))

            # 设置报错：如果当前点超出图像范围，跳出循环
            if x < 0 or y < 0 or x >= img.shape[1] or y >= img.shape[0]:
                break

            # 计算当前点的灰度值并添加到列表中
            gray_value = img[y, x]
            gray_values.append(gray_value)

        return gray_values

    def radial_profile_mean_variance(self, img, center, new_radius):
        # 创建一个数组，存储每个半径对应的灰度平均值和方差
        gray_values = []
        variances = []

        # 计算每个像素的灰度值
        for i in range(new_radius + 1):
            # 创建一个数组，存储当前半径上所有像素的灰度值
            gray_values_at_radius = []

            for j in range(360):
                # 将方向角度转换为弧度
                direction_angle_radians = np.deg2rad(j)

                # 计算当前点的坐标，从中心点开始，包括半径所在的一圈像素
                x = int(center[0] + i * np.cos(direction_angle_radians))
                y = int(center[1] + i * np.sin(direction_angle_radians))

                # 设置报错：如果当前点超出图像范围，跳出循环
                if x < 0 or y < 0 or x >= img.shape[1] or y >= img.shape[0]:
                    break

                # 计算当前点的灰度值并添加到列表中
                gray_value = img[y, x]
                gray_values_at_radius.append(gray_value)

            # 计算当前半径上所有像素的灰度平均值和方差并添加到列表中
            gray_values.append(np.mean(gray_values_at_radius))
            variances.append(np.var(gray_values_at_radius))

        return gray_values, variances


@st.cache_data(experimental_allow_widgets=True)
def get_coffee_ring_center(img):
    '''
    :param img: array
    :return: int
    '''
    st.subheader(":straight_ruler: 找到咖啡环中心与最大轮廓")  # 📏
    col1, col2 = st.columns([35, 65])

    with col1:
        # 添加输入框，用于传入近似中点的坐标， 默认为图片中心
        point_center = st.text_input('请输入一个**近似的中心点**坐标 x, y :',
                                     value=f'{img.shape[1] // 2}, {img.shape[0] // 2}')
        try:
            point_x, point_y = map(int, point_center.split(','))
        except ValueError:
            st.warning("请输入有效的坐标")

        # 获取点击点的颜色
        color = img[point_y, point_x]
        # 添加颜色阈值选择滑块
        color_threshold = st.slider("颜色阈值范围（±）", min_value=1, max_value=50, value=20)
        lower_bound = np.array([color[0] - color_threshold, color[1] - color_threshold, color[2] - color_threshold])
        upper_bound = np.array([color[0] + color_threshold, color[1] + color_threshold, color[2] + color_threshold])

        # 使用颜色阈值来筛选出符合条件的区域
        mask = cv2.inRange(img, lower_bound, upper_bound)
        # 渲染将阈值筛选后的图像
        st.image(mask, caption='mask of origin image')

        # 寻找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # 最大轮廓
            largest_contour = max(contours, key=cv2.contourArea)

            # 计算最小外接圆
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            center = (int(x), int(y))
            radius = int(radius)

            # 设置一个新的半径
            new_radius = st.number_input("修改**半径**让咖啡环完全进入mask选区", min_value=0, max_value=200,
                                         value=int(radius * 1.2))

    with col2:
        st.write(f'<center>计算mask内最小外接圆的圆心坐标位置为：{int(x)}, {int(y)}<center>', unsafe_allow_html=True)
        # 画出圆心，mask圆和新的mask圆
        img_copy = img.copy()
        cv2.circle(img_copy, center, 3, (0, 0, 255), -1)
        # cv2.circle(img_copy, center, radius, (0, 255, 0), 1)
        cv2.circle(img_copy, center, new_radius, (0, 0, 255), 1)
        # 渲染
        fig, axs = plt.subplots(nrows=2, ncols=2)
        axs[0, 0].set_title('RGB图像')
        axs[0, 0].imshow(img_copy)
        axs[0, 1].set_title('R channel')
        axs[0, 1].imshow(img_copy[:, :, 0])
        axs[1, 0].set_title('G channel')
        axs[1, 0].imshow(img_copy[:, :, 1])
        axs[1, 1].set_title('B channel')
        axs[1, 1].imshow(img_copy[:, :, 2])

        plt.tight_layout()
        st.pyplot(fig)

    return center, new_radius


@st.cache_data(experimental_allow_widgets=True)
def get_radial_profile_data(img, file_name, scale, center, radius):
    '''
    :param center: tuple
    :param radius: int
    :param img: array
    :return:
    '''
    st.subheader(":straight_ruler: 提取咖啡环径向分布的像素灰度值数据")  # 📏

    # 实例化之前定义的径向像素值强度分布计算类
    calculator = RadialProfileCalculator()
    # 3个通道数据
    R_gray_values, R_variances = calculator.radial_profile_mean_variance(img[:, :, 0], center, radius)
    G_gray_values, G_variances = calculator.radial_profile_mean_variance(img[:, :, 1], center, radius)
    B_gray_values, B_variances = calculator.radial_profile_mean_variance(img[:, :, 2], center, radius)

    # 绘制灰度值随半径的变化曲线
    L = np.arange(0, radius + 1)
    # 创建一个带有两个y轴的图
    fig, ax1 = plt.subplots()
    # 创建第二个y轴
    ax2 = ax1.twinx()
    # 设置标题与坐标轴标签
    plt.title('灰度值随半径的变化曲线\n'
              '')
    ax1.set_xlabel('Radius (pixels)')
    ax1.set_ylabel('Gray Value')
    ax2.set_ylabel('Variance')
    # 绘制曲线
    ax1.plot(L, R_gray_values, label='R channel', color='#dc565a')
    ax1.plot(L, G_gray_values, label='G channel', color='#56dc95')
    ax1.plot(L, B_gray_values, label='B channel', color='#569ddc')
    ax2.plot(L, R_variances, '--', label='R channel variance', color='#e6878a')
    ax2.plot(L, G_variances, '--', label='G channel variance', color='#87e6b4')
    ax2.plot(L, B_variances, '--', label='B channel variance', color='#87b9e6')

    # 将图例合并
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    # 渲染
    ax1.legend(handles, labels)
    plt.tight_layout()
    st.pyplot(fig)

    # -----💾-----
    # 添加输入框，用于传入保存目录
    save_dir = st.text_input("输入保存文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")

    # 添加按钮，用于保存数据
    if st.button('保存图片与数据'):
        # ---保存图片---
        fig.savefig(os.path.join(save_dir, f'{file_name[:-4]}_RadialProfile.png'), dpi=300)
        st.success("图像保存成功！")

        # ---保存数据到excel---
        # 将gray_values, variances保存到sheet1中
        df1 = pd.DataFrame({'radius': L.tolist(), 'R_gray_values': R_gray_values, 'R_variances': R_variances,
                            'G_gray_values': G_gray_values, 'G_variances': G_variances,
                            'B_gray_values': B_gray_values, 'B_variances': B_variances})
        # 将center, radius保存到sheet2中
        df2 = pd.DataFrame({'center(x, y)': list(center), 'radius (pixel)': radius, 'scale (mm/pixel)': scale})
        writer = pd.ExcelWriter(os.path.join(save_dir, f'{file_name[:-4]}_RadialProfile.xlsx'), engine='xlsxwriter')
        df1.to_excel(writer, sheet_name='gray_values', index=False)
        df2.to_excel(writer, sheet_name='circle', index=False)
        writer.save()
        st.success("数据保存成功！")

    return None


def main():
    st.title(":rainbow: 数据预处理——咖啡环图像处理")  # 🌈
    # 1.0-----上传图片-----
    img, file_name = load_data()
    if img is not None:
        # 2.0-----获取图片坐标板块-----
        get_img_coordinates(img)
        # 3.0-----计算像素与实际距离的比例-----
        scale = actual_size_mapping(img)
        # 4.0-----找到咖啡环中心与最大轮廓-----
        center, radius = get_coffee_ring_center(img)
        # 5.0-----提取咖啡环径向分布的像素灰度值数据-----
        get_radial_profile_data(img, file_name, scale, center, radius)


if __name__ == "__main__":
    main()
