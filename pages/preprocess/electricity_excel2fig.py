"""将同一文件夹内的所有电学测试数据（除电阻）的Excel文件进行画图"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def CV_plot(df, curve_label, save_path):
    # 提取数据，考虑到keithley的CV数据无法提取时间则不画时间轴
    potential = df['Potential[V]']
    current = df['Current[A]']

    # 画图
    plt.figure()
    plt.plot(potential, current, label=curve_label)

    plt.xlabel('Potential[V]')
    plt.ylabel('Current[A]')
    # 使用科学计数法表示纵轴坐标
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return st.success(f'CV_plot PNG saved to {save_path}')


def It_CA_plot(df, curve_label, save_path):
    # 提取数据
    time = df['Time[s]']
    potential = df['Potential[V]']
    current = df['Current[A]']

    # 画图
    fig = plt.figure(figsize=(4, 5))  # 根据需要调整 figsize
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])  # 子图高度比例

    # 在第一个子图中绘制电压随时间变化的图形
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(time, potential, label=curve_label)
    ax1.set_xlabel('Time[s]')
    ax1.set_ylabel('Potential[V]')

    # 在第二个子图中绘制电流随时间变化的图形（主要）
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(time, current, label=curve_label)
    ax2.set_xlabel('Time[s]')
    ax2.set_ylabel('Current[A]')
    # 使用科学计数法表示纵轴坐标
    ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    plt.subplots_adjust(hspace=0.3)  # 调整子图之间的间距
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return st.success(f'It_CA_plot PNG saved to {save_path}')


def Vt_plot(df, curve_label, save_path):
    # 提取数据
    time = df['Time[s]']
    potential = df['Potential[V]']
    current = df['Current[A]']

    # 画图
    fig = plt.figure(figsize=(4, 5))  # 根据需要调整 figsize
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 3])  # 子图高度比例

    # 在第一个子图中绘制电流随时间变化的图形
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(time, current, label=curve_label)
    ax1.set_xlabel('Time[s]')
    ax1.set_ylabel('Current[A]')
    # 使用科学计数法表示纵轴坐标
    ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    # 在第二个子图中绘制电压随时间变化的图形（主要）
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(time, potential, label=curve_label)
    ax2.set_xlabel('Time[s]')
    ax2.set_ylabel('Potential[V]')
    # 使用科学计数法表示纵轴坐标
    # ax2.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    plt.subplots_adjust(hspace=0.3)  # 调整子图之间的间距
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return st.success(f'Vt_plot PNG saved to {save_path}')


def OCP_plot(df, curve_label, save_path):
    time = df['Time[s]']
    potential = df['Potential[V]']

    # 画图
    plt.figure()
    plt.plot(time, potential, label=curve_label)

    plt.xlabel('Time[s]')
    plt.ylabel('Potential[V]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    return st.success(f'OCP_plot PNG saved to {save_path}')


def single_curve(folder_path):
    """一个数据一个图"""
    single_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    # 提前设置图形属性，避免重复
    plt.rcParams['font.sans-serif'] = ['simhei']
    plt.rcParams['axes.unicode_minus'] = False

    for single_file_name in single_files:
        single_file_path = os.path.join(folder_path, single_file_name)
        # 读取excel文件数据
        workbook = pd.ExcelFile(single_file_path)
        sheet_name = workbook.sheet_names[0]
        df = workbook.parse(sheet_name)
        # 获取file_name，即电学曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]
        # 图片保存路径
        save_path = os.path.join(folder_path, single_file_path.replace('.xlsx', '.png'))

        if 'CV' in single_file_name:
            CV_plot(df, curve_label, save_path)
        elif 'It' in single_file_name or 'CA' in single_file_name:
            It_CA_plot(df, curve_label, save_path)
        elif 'Vt' in single_file_name:
            Vt_plot(df, curve_label, save_path)
        elif 'OCP' in single_file_name:
            OCP_plot(df, curve_label, save_path)

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    st.warning('根据文件名自动区分CV/It/CA/Vt')

    # ---按mode执行---
    if st.button('运行画图程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in
                          os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                single_curve(subfolder)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            single_curve(excel_folder)

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——CV/It/CA.excel数据画图")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
