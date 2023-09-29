import streamlit as st
from PIL import Image
import numpy as np
import streamlit_image_coordinates as sic
import matplotlib.pyplot as plt
import cv2
import os
import pandas as pd
import pyperclip
import math


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    """返回图像的数组和文件名
    """
    uploaded_file = st.file_uploader('请选择一张图片上传', type=["jpg", "png"])
    # 返回图像和文件名
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img = np.asarray(image)
        file_name = uploaded_file.name
        return img, file_name
    else:
        return None, None


def get_img_coordinates(img):
    """使用streamlit_image_coordinates库，渲染图片，并返回鼠标点击图像像素点的坐标
    :param img: array
    """
    st.subheader(":point_down: 图像像素点位置获取面板")  # 👇
    value = sic.streamlit_image_coordinates(img, key="pil")
    if value is not None:
        point_x = value["x"]
        point_y = value["y"]
        st.write(f'点击上图获取的坐标位置为：{point_x}, {point_y}')
        # 将坐标点复制到剪贴板
        pyperclip.copy(f'{point_x}, {point_y}')
        st.success(f'{point_x}, {point_y}已复制到剪切板')
    else:
        st.write(':+1:请点击上方图片选择一个像素点')  # 👍
    return None


@st.cache_data(experimental_allow_widgets=True)
def actual_size_mapping(img):
    """通过在图片上标记两个已知实际距离的像素点，计算出像素与实际距离的比例
    """
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


class RadialProfileCalculator:
    """定义一个提取咖啡环图片颜色变化的类
    """

    def radial_profile_direction(self, img, center, new_radius, direction_angle_degrees):
        """计算从圆心到新的圆，在指定方向上的灰度平均值随半径的变化
        """
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
        """创建一个数组，存储每个半径对应的灰度平均值和方差(标准差)
        """
        gray_values = []
        # variances = []
        standard_deviation = []

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
            # variances.append(np.var(gray_values_at_radius))  # 方差
            standard_deviation.append(np.std(gray_values_at_radius))  # 标准差

        return gray_values, standard_deviation


class CalculateCircleCenter:
    """定义一个计算圆心的类"""

    def center_from_mask(self, mask):
        """通过mask计算最小外接圆的圆心坐标
        """
        # 寻找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # 最大轮廓
            largest_contour = max(contours, key=cv2.contourArea)

            # 计算最小外接圆
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            center = (int(x), int(y))
            radius = int(radius)
        else:
            center = None
            radius = None

        return center, radius

    def center_from_3point(self, point1, point2, point3):
        """通过3点坐标计算圆心坐标，返回圆心坐标和半径
        """
        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = point3

        # 计算圆心坐标
        d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        ux = ((x1 ** 2 + y1 ** 2) * (y2 - y3) + (x2 ** 2 + y2 ** 2) * (y3 - y1) + (x3 ** 2 + y3 ** 2) * (y1 - y2)) / d
        uy = ((x1 ** 2 + y1 ** 2) * (x3 - x2) + (x2 ** 2 + y2 ** 2) * (x1 - x3) + (x3 ** 2 + y3 ** 2) * (x2 - x1)) / d
        center = (int(ux), int(uy))

        # 计算半径
        radius = math.sqrt((x1 - ux) ** 2 + (y1 - uy) ** 2)
        radius = int(radius)

        return center, radius


@st.cache_data(experimental_allow_widgets=True)
def get_coffee_ring_center(img):
    """找到咖啡环中心与最大轮廓的web部件
    """
    st.subheader(":straight_ruler: 找到咖啡环中心与最大轮廓")  # 📏
    col1, col2 = st.columns([35, 65])

    with col1:
        center_method = st.radio("选择计算圆心的方法", ["阈值mask法计算圆心", "3点法计算圆心"])

        if center_method == "阈值mask法计算圆心":
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

            # 计算的圆心坐标和半径
            center, radius = CalculateCircleCenter().center_from_mask(mask)

        elif center_method == "3点法计算圆心":
            # 添加输入框，用于传入三个点的坐标
            point1 = st.text_input('请输入point1坐标点 x, y :', value=f'{img.shape[1] // 3}, {img.shape[0] // 3}')
            point2 = st.text_input('请输入point2坐标点 x, y :', value=f'{img.shape[1] // 2}, {img.shape[0] // 2}')
            point3 = st.text_input('请输入point3坐标点 x, y :',
                                   value=f'{img.shape[1] // 3 * 2}, {img.shape[0] // 3 * 2}')

            try:
                point1_x, point1_y = map(int, point1.split(','))
                point2_x, point2_y = map(int, point2.split(','))
                point3_x, point3_y = map(int, point3.split(','))
            except ValueError:
                st.warning("请输入有效的坐标")

            # 在图像上标记三个点
            img_copy = img.copy()
            cv2.circle(img_copy, (point1_x, point1_y), 3, (255, 0, 0), -1)
            cv2.circle(img_copy, (point2_x, point2_y), 3, (255, 0, 0), -1)
            cv2.circle(img_copy, (point3_x, point3_y), 3, (255, 0, 0), -1)
            # 渲染
            st.image(img_copy, caption='3 points of origin image')

            # 计算的圆心坐标和半径
            center, radius = CalculateCircleCenter().center_from_3point((point1_x, point1_y),
                                                                        (point2_x, point2_y),
                                                                        (point3_x, point3_y))

    with col2:
        # 自定义新的圆心
        customization = st.checkbox('自定义圆心')
        if customization:
            # 添加输入框，用于传入新的圆心坐标
            new_center = st.text_input('请输入新的圆心坐标 x, y :', value=f'{center[0]}, {center[1]}')
            try:
                new_center_x, new_center_y = map(int, new_center.split(','))
            except ValueError:
                st.warning("请输入有效的坐标")
            # 设置新的圆心
            center = (new_center_x, new_center_y)

        # 设置一个新的半径
        new_radius = st.number_input("修改**半径**获取咖啡环最大轮廓", min_value=0, max_value=500,
                                     value=int(radius * 1.2))
        # 打印计算返回的圆心坐标
        st.write(f'<center>计算得到的圆心坐标位置为：{center[0]}, {center[1]}<center>', unsafe_allow_html=True)
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
    """提取咖啡环径向分布的像素灰度值数据
    """
    st.subheader(":straight_ruler: 提取咖啡环径向分布的像素灰度值数据")  # 📏

    # 实例化之前定义的径向像素值强度分布计算类
    calculator = RadialProfileCalculator()
    # 3个通道数据
    R_gray_values, R_standard_deviation = calculator.radial_profile_mean_variance(img[:, :, 0], center, radius)
    G_gray_values, G_standard_deviation = calculator.radial_profile_mean_variance(img[:, :, 1], center, radius)
    B_gray_values, B_standard_deviation = calculator.radial_profile_mean_variance(img[:, :, 2], center, radius)

    # ---绘制灰度值随半径的变化曲线---
    L = np.arange(0, radius + 1)
    # 使用gridspec界面进行复杂图排版
    fig = plt.figure()
    grid = plt.GridSpec(6, 4)
    # 创建一个带有两个y轴的图
    ax1 = fig.add_subplot(grid[0:4, 0:4])
    # 创建第二个y轴
    ax2 = ax1.twinx()
    # 设置标题与坐标轴
    ax1.set_title('灰度值随半径的变化曲线')
    ax1.set_xticks(np.arange(0, radius + 11, 10))  # 设置x轴坐标间隔为10
    ax1.set_xlabel('Radius (pixels)')
    ax1.set_ylabel('Gray Value')
    ax2.set_ylabel('Standard Deviation')
    # 绘制曲线
    ax1.plot(L, R_gray_values, label='R gray_values', color='#dc565a')
    ax1.plot(L, G_gray_values, label='G gray_values', color='#56dc95')
    ax1.plot(L, B_gray_values, label='B gray_values', color='#569ddc')
    ax2.plot(L, R_standard_deviation, '--', label='R standard_deviation', color='#e6878a')
    ax2.plot(L, G_standard_deviation, '--', label='G standard_deviation', color='#87e6b4')
    ax2.plot(L, B_standard_deviation, '--', label='B standard_deviation', color='#87b9e6')

    # 将图例合并
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    ax1.legend(handles, labels)

    # ---将Img裁切到只有mask最小外接矩形大小和位置---
    # 创建与输入图像相同大小的全零掩码
    mask = np.zeros_like(img)
    # 创建一个白色填充的圆形掩码
    cv2.circle(mask, center, radius, (255, 255, 255), thickness=cv2.FILLED)
    # 执行按位与（AND）操作，保留都有值的部分
    masked_img = cv2.bitwise_and(img, mask)
    # 计算新图像的左上角坐标
    (new_x, new_y) = (center[0] - radius, center[1] - radius)
    # 计算新图像的右下角坐标
    new_width = new_height = 2 * radius
    # 使用切片获取最小外接正方形
    cropped_masked_img = masked_img[new_y:new_y + new_height, new_x:new_x + new_width]
    r, g, b = cv2.split(cropped_masked_img)

    # 继续在fig上使用graidspec排版
    axrgb = fig.add_subplot(grid[4:6, 0])
    axrgb.set_title('rgb image')
    axrgb.imshow(cropped_masked_img)
    axrgb.axis('off')
    axr = fig.add_subplot(grid[4:6, 1])
    axr.set_title('R channel')
    axr.imshow(r, cmap='gray')
    axr.axis('off')
    axg = fig.add_subplot(grid[4:6, 2])
    axg.set_title('G channel')
    axg.imshow(g, cmap='gray')
    axg.axis('off')
    axb = fig.add_subplot(grid[4:6, 3])
    axb.set_title('B channel')
    axb.imshow(b, cmap='gray')
    axb.axis('off')
    # 渲染
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
        df1 = pd.DataFrame({'radius': L.tolist(), 'R_gray_values': R_gray_values, 'R_variances': R_standard_deviation,
                            'G_gray_values': G_gray_values, 'G_variances': G_standard_deviation,
                            'B_gray_values': B_gray_values, 'B_variances': B_standard_deviation})
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
