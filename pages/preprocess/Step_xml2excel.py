"""将台阶仪的xml测试数据转换为Excel文件"""
import pandas as pd
import re
import streamlit as st
import os
import xml.etree.ElementTree as ET


def step_xml2excel(file_path):
    # 读取并解析XML文件
    tree = ET.parse(file_path)
    root = tree.getroot()
    data = []

    # 提取X和Z的单位
    x_units = root.find('.//XUnits').text
    z_units = root.find('.//ZUnits').text

    # 提取数据
    for elem in root.find('.//DataBlock'):
        x = float(elem.find('X').text)
        z = float(elem.find('Z').text)
        data.append({f'X ({x_units})': x, f'Z ({z_units})': z})

    # 将数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 将数据保存为Excel文件，包含处理后的第一行，指定工作表名称为文件名
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    excel_output_path = os.path.splitext(file_path)[0] + '.xlsx'
    with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, index=False, header=True, startrow=0, sheet_name='Step_rawdata')  # 从第一行开始写入数据，包含标题行
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name],})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有xml', '模式二：处理单个文件夹下的所有xml', '模式三：处理单个xml'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有xml':
        txt_farther_folder = st.text_input("输入xml所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有xml':
        txt_folder = st.text_input("输入xml所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个xml':
        txt_path = st.text_input("输入xml的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\kei.txt**")


    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有xml':
            # 获取所有txt文件的路径
            txt_files = [os.path.join(root, file) for root, _, files in os.walk(txt_farther_folder) for file in files if
                         file.endswith('.xml')]
            # 处理每个txt文件
            for file_path in txt_files:
                step_xml2excel(file_path)
        elif mode == '模式二：处理单个文件夹下的所有xml':
            txt_files = [os.path.join(txt_folder, file) for file in os.listdir(txt_folder) if file.endswith('.xml')]
            for file_path in txt_files:
                step_xml2excel(file_path)
        elif mode == '模式三：处理单个xml':
            step_xml2excel(txt_path)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——Step.xml文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
