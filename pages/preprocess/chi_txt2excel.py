"""将chi电化学工作站的txt测试数据转换为Excel文件"""
import pandas as pd
import streamlit as st
import os
import re


def find_data_start_line(content, keywords):
    """
    查找包含指定关键词的行号
    :param content: 文件内容列表
    :param keywords: 要查找的关键词列表
    :return: 包含所有关键词的行号，如果未找到，返回None
    """
    for i, line in enumerate(content):
        if all(keyword in line for keyword in keywords):
            return i + 2  # 数据从关键词行的下2行开始
    return None


def extract_scan_rate(content):
    """
    提取扫描速率和其他参数
    :param content: 文件内容
    :return: 扫描速率
    """
    scan_rate = None
    experiment_time = None
    parameters = {}

    # 使用正则表达式提取扫描速率和实验时间等参数
    for line in content:
        if 'Scan Rate (V/s)' in line:
            scan_rate = re.search(r'Scan Rate \(V/s\) = ([\d.]+)', line)
            if scan_rate:
                parameters['Scan Rate (V/s)'] = scan_rate.group(1)
    return parameters


def chi_txt2excel(file_path, columns):
    """处理CHI的txt文件，转换为Excel"""
    # 读取文件内容
    with open(file_path, 'r') as file:
        content = file.readlines()

    # 匹配第二行的模式
    scan_mode_line = content[1].strip()

    # 定义不同扫描模式的关键词
    if '开路电位-时间' in scan_mode_line:
        scan_model = 'OCP'
        columns = ['Time[s]', 'Potential[V]']
        keywords = ['Time/sec, Potential/V']
    elif '线性扫描伏安法' in scan_mode_line:
        scan_model = 'LSV'
        columns = ['Potential[V]', 'Current[A]']
        keywords = ['Potential/V, Current/A']
    elif '循环伏安法' in scan_mode_line:
        scan_model = 'CV'
        columns = ['Potential[V]', 'Current[A]']
        keywords = ['Potential/V, Current/A']

    # 通过关键词查找数据的起始行
    data_start_line = find_data_start_line(content, keywords)

    # 提取数据
    data = [[float(value) for value in line.split(',')] for line in content[data_start_line:]]

    # 创建DataFrame
    df = pd.DataFrame(data, columns=columns)

    #
    if scan_model == 'CV':
        scan_rate = extract_scan_rate(content).get('Scan Rate (V/s)', 'Unknown')  # 提取扫描速率
        time_interval = (float(df.iloc[2, 0]) - float(df.iloc[1, 0]))/float(scan_rate)
        # 新增 'time[s]' 列，数据为索引乘以time_interval
        df.insert(0, 'Time[s]', df.index * time_interval)

    # 将数据保存为Excel文件，包含处理后的第一行，指定工作表名称为文件名
    file_name = file_path.split('.txt')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.txt', f'{scan_model}_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, header=True, startrow=0, sheet_name=scan_model)  # 从第一行开始写入数据，包含标题行
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有txt', '模式二：处理单个文件夹下的所有txt', '模式三：处理单个txt'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有txt':
        txt_farther_folder = st.text_input(
            "输入txt所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
        st.warning('需要保证该目录下所有子文件夹内的txt为CHI的文件')
    elif mode == '模式二：处理单个文件夹下的所有txt':
        txt_folder = st.text_input("输入txt所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
        st.warning('需要保证该目录下所有子文件夹内的txt为CHI的文件')
    elif mode == '模式三：处理单个txt':
        txt_path = st.text_input("输入txt的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\kei.txt**")

    # ---colunms选择---
    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        columns_select = st.selectbox('选择原始txt对应的**所有列名**选项',
                                      ('Potential[V], Current[mA]',
                                       'time[s], Potential[V], Current[mA]'))
        st.warning('已实现**CV、LSV、OCP**的自动数据处理')
    with col2:
        columns_input = st.text_input('可自定义输入**所有列名**（需用英文逗号隔开），例如：Potential[V], Current[mA]')
    if columns_input:
        columns = [col.strip() for col in columns_input.split(',')]
    else:
        columns = [col.strip() for col in columns_select.split(',')]
    # st.text(columns)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有txt':
            # 获取所有txt文件的路径
            txt_files = [os.path.join(root, file) for root, _, files in os.walk(txt_farther_folder) for file in files if
                         file.endswith('.txt')]
            # 处理每个txt文件
            for file_path in txt_files:
                chi_txt2excel(file_path, columns=columns)
        elif mode == '模式二：处理单个文件夹下的所有txt':
            txt_files = [os.path.join(txt_folder, file) for file in os.listdir(txt_folder) if file.endswith('.txt')]
            for file_path in txt_files:
                chi_txt2excel(file_path, columns=columns)
        elif mode == '模式三：处理单个txt':
            chi_txt2excel(txt_path, columns=columns)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——CHI.txt文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
