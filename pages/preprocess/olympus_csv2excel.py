import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt


def csv2excel(file_path, heatmap_fig):
    # 读取csv文件注释信息
    df_title = pd.read_csv(file_path, delimiter=',', nrows=10)
    file_name = df_title.iloc[0, 1].split('.poir')[0].split('\\')[-1]  # 提取文件名
    data_type = df_title.iloc[1, 1]  # 高度or强度
    resolution = df_title.iloc[2, 1]  # 分辨率
    # 提取2维图数据
    df = pd.read_csv(file_path, delimiter=',', header=18, index_col=0)
    df = df.iloc[:, :-1]  # 删除最后一列Nan
    # 修改列标题
    new_columns = [f'{data_type}{i}' for i in range(len(df.columns))]
    df.columns = new_columns

    # 将 DataFrame 保存为 Excel 文件
    dir_name = os.path.dirname(file_path)
    excel_output_path = os.path.join(dir_name, f'Confocal{data_type}_{file_name}.xlsx')
    with pd.ExcelWriter(excel_output_path) as writer:
        # 将 df 保存到名为 scan_mode 的 sheet 中
        df.to_excel(writer, sheet_name=f'Confocal{data_type}', index=False)
        # 创建包含参数的 DataFrame，将filename保存到名为 'parameter' 的 sheet 中
        parameters = pd.DataFrame({'File Name': [file_name]})
        parameters.to_excel(writer, sheet_name='parameter', index=False)



    st.success(f"Excel file saved to {excel_output_path}")

    if heatmap_fig:
        plt.figure()
        plt.imshow(df, cmap='viridis', interpolation='nearest')
        if data_type == 'Height':
            plt.colorbar(label='µm')  # 添加颜色条并指定单位
        elif data_type == 'Intensity':
            plt.colorbar()
        plt.title(f"{data_type} heatmap of {file_name} \n x,y resolution: {resolution}µm")
        plt.tight_layout()
        plt.savefig(excel_output_path.replace('.xlsx', '.png'), dpi=300)
        plt.close()
        st.success(f'PNG {file_name} saved')

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有csv', '模式二：处理单个文件夹下的所有csv', '模式三：处理单个csv'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有csv':
        csv_farther_folder = st.text_input(
            "输入csv所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有csv':
        csv_folder = st.text_input("输入csv所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    elif mode == '模式三：处理单个csv':
        csv_path = st.text_input("输入csv的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\olympus.csv**")

    # ---heatmap---
    heatmap_fig = st.checkbox('是否画出共聚焦热力图', value=True)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有csv':
            csv_files = [os.path.join(root, file) for root, _, files in os.walk(csv_farther_folder) for file in
                         files if file.endswith('.csv')]
            for file_path in csv_files:
                csv2excel(file_path, heatmap_fig)
        elif mode == '模式二：处理单个文件夹下的所有csv':
            csv_files = [os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]
            for file_path in csv_files:
                csv2excel(file_path, heatmap_fig)
        elif mode == '模式三：处理单个csv':
            csv2excel(csv_path, heatmap_fig)

    return None


def st_main():
    st.title(":repeat_one: 数据预处理——olympus.csv文件转excel文件")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
