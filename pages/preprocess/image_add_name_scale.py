"""
将图片名称添加到图片左上角，将比例尺添加到图片右下角
"""
import streamlit as st
import os
from PIL import Image, ImageDraw, ImageFont
import re


pixel_scale_dict = {'海康(2*2merge)-凤凰-X5': 0.745, '海康(2*2merge)-凤凰-X10': 0.3725,
                    '海康(2*2merge)-凤凰-X20': 0.18625,
                    '海康(2*2merge)-凤凰-X40': 0.093125, '海康(2*2merge)-凤凰-X60': 0.062083333,
                    '凤凰-凤凰-X5': 1.345, '凤凰-凤凰-X10': 0.6725, '凤凰-凤凰-X20': 0.33625,
                    '凤凰-凤凰-X40': 0.168125, '凤凰-凤凰-X60': 0.112083333}


def get_lens_parameter(file_path):
    # 使用正则表达式提取 '-'/'_' 和 'x'/'X' 之间的整数或浮点数
    result = re.search(r'[-_](\d+(\.\d+)?)[xX]', file_path)
    if result:
        extracted_number = result.group(1)
        return extracted_number
    else:
        return '未提取到放大倍数'


def png_add_name_scale(png_path, text_parameters, scale_parameters):
    # 参数解析
    [text_color, font_size, font_path] = text_parameters
    if len(scale_parameters) > 0:
        [camera, microscope, lens, lens_extract, pixels] = scale_parameters
        if lens_extract:
            lens = get_lens_parameter(png_path)

    # 创建字体对象
    font = ImageFont.truetype(font_path, font_size)
    text_color = text_color

    # 打开图片
    image = Image.open(png_path)
    width, height = image.size
    # 创建绘图对象
    draw = ImageDraw.Draw(image)

    # 获取图片名称（不带文件扩展名）
    image_name = os.path.splitext(png_path)[0].split('\\')[-1]
    # 在左上角添加文本
    draw.text((10, 10), image_name, fill=text_color, font=font)

    # 绘制右下角比例尺
    if len == '未提取到放大倍数':
        st.error(f'{png_path}未提取到放大倍数')
    else:
        pixel_scale = pixel_scale_dict[f'{camera}-{microscope}-X{lens}']
    # 添加比例尺信息
    draw.text((width - 180, height - 50), f'{pixel_scale * pixels:.3f}μm', fill=text_color, font=font)
    # 绘制直线
    end_point = (width - 20, height - 55)
    start_point = (end_point[0] - pixels, end_point[1])
    draw.line([start_point, end_point], fill=text_color, width=2)  # 可以设置直线的颜色和宽度

    # 保存带有文本的图片
    image.save(png_path)
    # 关闭图片
    image.close()
    return st.success(f'已添加名称与比例尺到{png_path}')


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有png/jpg图片', '模式二：处理单个文件夹下的所有png/jpg图片',
                     '模式三：处理单个png/jpg图片'], index=2)
    if mode == '模式一：处理所有子文件夹内的所有png/jpg图片':
        png_farther_folder = st.text_input(
            "输入png所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有png/jpg图片':
        png_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个png/jpg图片':
        png_path = st.text_input("输入png的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\image.png**")

    # ---文字大小颜色选择---
    col1, col2, col3 = st.columns(3)
    text_color = col1.color_picker('选择文本颜色', value='#ff0004')
    font_size = col2.number_input('输入文本大小', value=36)
    font_path = col3.text_input('输入字体文件路径', value='C:/Windows/Fonts/simhei.ttf')
    text_parameters = [text_color, font_size, font_path]

    # ---比例尺选择---
    scale_check = st.checkbox('是否添加比例尺', value=False)
    if scale_check:
        col1, col2, col3, col4 = st.columns(4)
        camera = col1.selectbox('选择拍摄使用的相机', ['海康(2*2merge)', '凤凰'], index=0)
        microscope = col2.selectbox('选择拍摄使用显微镜', ['凤凰', '海约'], index=0)
        if microscope == '凤凰':
            lens = col3.selectbox('选择物镜放大的倍数', ['5', '10', '20', '40', '60'], index=0)
        elif microscope == '海约':
            lens = col3.selectbox('选择显微镜放大的倍数', ['5', '10'], index=0)
        lens_extract = col3.checkbox('从文件名提取放大倍数，文件名包含**_5x**等', value=False)
        # scale = col4.number_input('输入比例尺的基本单位长度[um]', value=100)
        pixels = col4.number_input('输入比例尺的基本单位长度[pixels]', value=50)
        scale_parameters = [camera, microscope, lens, lens_extract, pixels]
    else:
        scale_parameters = []

    # ---按mode执行---
    if st.button('运行图片处理程序'):
        if mode == '模式一：处理所有子文件夹内的所有png/jpg图片':
            png_files = [os.path.join(root, file) for root, _, files in os.walk(png_farther_folder) for file in
                         files if file.endswith(('.png', '.jpg'))]
            for file_path in png_files:
                png_add_name_scale(file_path, text_parameters, scale_parameters)
        elif mode == '模式二：处理单个文件夹下的所有png/jpg图片':
            png_files = [os.path.join(png_folder, file) for file in os.listdir(png_folder) if
                         file.endswith(('.png', '.jpg'))]
            for file_path in png_files:
                png_add_name_scale(file_path, text_parameters, scale_parameters)
        elif mode == '模式三：处理单个png/jpg图片':
            png_add_name_scale(png_path, text_parameters, scale_parameters)

    return None


def st_main():
    st.title(":cinema: 数据预处理——image添加名称与比例尺")  # 🎦
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
