"""将双光束紫外分光光度计的sca数据转换为Excel文件"""
import pandas as pd
import streamlit as st
import os


def absorbance_to_transmittance(absorbance):
    return 10 ** (-absorbance)


def normalize_data(series):
    """归一化给定的Pandas Series到0-1之间。"""
    min_value = series.min()
    max_value = series.max()
    return (series - min_value) / (max_value - min_value)


def sca2excel(file_path, spectrum):
    """注意起始行与结束行的处理"""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # 获取数据开始的行数，即第一个以 'Filter:10' 开头的行
    for i, line in enumerate(lines):
        if line.startswith('Filter:10'):
            start_row = i + 1
            break

    # 从数据开始的行数开始读取数据，直到 '[Extended]' 结束
    data = []
    for line in lines[start_row:]:
        if line.startswith('[Extended]'):
            break
        data.append(line.strip().split(' '))  # 空格分列

    # 将数据转换为DataFrame
    df = pd.DataFrame(data, columns=['Wavelength[nm]', spectrum])
    df = df.astype(float)

    # 根据需要转变吸光度为透过率
    if spectrum == 'Transmittance':
        # 从第二列开始，转换为透过率
        df.iloc[:, 1:] = df.iloc[:, 1:].apply(absorbance_to_transmittance)

    # 归一化光谱数据到0-1之间
    df['Normalized'] = normalize_data(df[spectrum])

    # 将 DataFrame 保存为 Excel 文件
    file_name = file_path.split('.sca')[0].split('\\')[-1]
    excel_output_path = file_path.replace(f'{file_name}.sca', f'{spectrum}_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path) as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, sheet_name=spectrum, index=False)
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)

    return st.success(f"Converted excel file saved to {excel_output_path}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有sca', '模式二：处理单个文件夹下的所有sca', '模式三：处理单个sca'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有sca':
        sca_farther_folder = st.text_input("输入sca所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有sca':
        sca_folder = st.text_input("输入sca所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个sca':
        sca_path = st.text_input("输入sca的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\uv.sca**")
    st.warning('请注意输入的路径与选择的模式相匹配')

    # ---spectrum选择---
    spectrum_check = st.checkbox('是否需要转换纵坐标为**透过率**？（原始为吸光度）', value=True)
    if spectrum_check:
        spectrum = 'Transmittance'
    else:
        spectrum = 'Absorbance'

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有sca':
            sca_files = [os.path.join(root, file) for root, _, files in os.walk(sca_farther_folder) for file in files if
                         file.endswith('.sca')]
            for file_path in sca_files:
                sca2excel(file_path, spectrum)
        elif mode == '模式二：处理单个文件夹下的所有sca':
            sca_files = [os.path.join(sca_folder, file) for file in os.listdir(sca_folder) if file.endswith('.sca')]
            for file_path in sca_files:
                sca2excel(file_path, spectrum)
        elif mode == '模式三：处理单个sca':
            sca2excel(sca_path, spectrum)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——uv.sca文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
