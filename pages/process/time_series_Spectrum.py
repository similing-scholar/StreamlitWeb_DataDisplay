"""时间序列的光谱数据，可视化分析与画图"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import os


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    uploaded_file = st.file_uploader("上传时间序列的光谱透过率数据Excel文件，通常为[**spectrum_yyyymmdd-.xlsx**]文件",
                                     type=["xlsx", "xls"])
    if uploaded_file is not None:
        # 读取 Excel 文件，获取sheet_name，并转化为dataframe
        workbook = pd.ExcelFile(uploaded_file)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取curve_name
        parameter_df = workbook.parse('parameter')
        curve_name = parameter_df['File Name'][0]
        # 获取file_name
        file_name = uploaded_file.name
        return df, curve_name, file_name
    else:
        return None, None, None


def data_transform(df):
    """将原始数据转置，方便后续操作"""
    # 将数据转置，行为时间，列为波长
    df_T = df.transpose()
    # 将转置后的DataFrame的第一行作为标题行
    df_T.columns = df_T.iloc[0]
    # 删除原始的标题行
    df_T = df_T[1:]
    return df_T


def time_point_plot(df, df_T, curve_name, filename):
    # ---选择单个波长来确定时间点---
    col1, col2 = st.columns([30, 70])
    with col1:
        # 选择波长
        selected_serial = st.slider('预览：选择单个波长来确定时间点', min_value=1, max_value=df_T.shape[1] - 1,
                                    value=1)  # 从第二列开始
        selected_column = df_T.columns[selected_serial]
        st.write(f'You selected {selected_column}')
        # 填写采样时间间隔
        sampling_interval = st.number_input('填写采样间隔[s]')
        # 自动获取采样时间间隔
        get_sampling_interval = st.checkbox('根据列名自动获取采样间隔', value=True)
        if get_sampling_interval:
            sampling_interval = float(df.columns[2][:-1]) - float(df.columns[1][:-1])  # 0.5s - 0.0s
            st.write(f'自动获取采样间隔为{sampling_interval}[s]')
        # np创建一个df行数的列表，作为时间轴
        time_axis = np.arange(df_T.shape[0]) * sampling_interval

    with col2:
        # 使用 Plotly 来预览曲线
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_axis, y=df_T[selected_column], mode='lines'))
        fig.update_layout(
            title=f'单个波长下的循环曲线',
            title_x=0.45,
            xaxis_title='Time[s]',
            yaxis_title='Transmission',
            xaxis_showgrid=True,  # 显示x轴网格线
            yaxis_showgrid=True,  # 显示y轴网格线
            height=400,  # 设置高度
            width=500,  # 设置宽度
        )
        st.plotly_chart(fig)

    # ---实际选择多个时间点来绘制曲线---
    col3, col4 = st.columns([30, 70])
    with col3:
        # 选择时间点
        selected_columns = st.multiselect('(可多选时间点)', df.columns[1:])
        st.write(f'You selected {selected_columns}')

        # 选择保存文件夹
        save_folder = st.text_input("输入保存文件夹的**绝对路径**，如C:\\Users\\JiaPeng\\Desktop")  # 【可修改】
        save_name = st.text_input("输入保存的名字，例如TimePlot_.png",
                                  value='TimePlot_'+filename.replace('.xlsx', '.png'))  # 【可修改】

    with col4:
        # 提取波长列作为x轴
        wavelength_column = df.iloc[:, 0]

        # 创建一个空的 DataFrame 用于保存数据
        data_to_save = pd.DataFrame()
        # 将波长列添加到要保存的 DataFrame 中
        data_to_save['Wavelength[nm]'] = wavelength_column

        # 绘制光谱曲线
        fig = plt.figure()
        for column in selected_columns:
            plt.plot(wavelength_column, df[column], label=column)
            data_to_save[column] = df[column].values  # 将数据添加到要保存的 DataFrame
        plt.title(f'Transmission spectrum curve at a certain time point (voltage) \n'
                  f'{curve_name}')
        plt.xlabel('Wavelength[nm]')
        plt.ylabel('transmittance')
        plt.legend(loc='upper left')  # 调整legend的位置到右侧
        fig.tight_layout()
        # 显示图形
        st.pyplot(fig)
        # 保存图形按钮
        if st.button("保存TimePlot为png格式"):
            if save_folder == '':
                st.warning("请先输入保存文件夹的绝对路径")
            else:
                fig.savefig(os.path.join(save_folder, save_name), dpi=300)
                st.success(f"图像保存在{save_folder}文件夹下")
        # 保存数据文件按钮
        if st.button("保存TimePlot数据为excel格式"):
            if save_folder == '':
                st.warning("请先输入保存文件夹的绝对路径")
            else:
                data_to_save.to_excel(os.path.join(save_folder, 'Data'+save_name.replace('.png', '.xlsx')), index=False)
                st.success(f"数据保存在{save_folder}文件夹下")

    return time_axis, save_folder


def wavelength_plot(df, df_T, time_axis, save_folder, curve_name, filename):
    # ---选择时间点来确定波长---
    col1, col2 = st.columns([30, 70])
    with col1:
        selected_serial = st.slider('预览：选择单个时间点来确定波长', min_value=1, max_value=df.shape[1] - 1,
                                    value=1)  # 从第二列开始
        selected_column = df.columns[selected_serial]
        st.write(f'You selected {selected_column}')

    with col2:
        # 使用 Plotly 来预览曲线
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.iloc[:, 0], y=df[selected_column], mode='lines'))
        fig.update_layout(
            title=f'单个时间点下的光谱',
            title_x=0.4,
            xaxis_title='Wavelength [nm]',
            yaxis_title='Transmission',
            xaxis_showgrid=True,  # 显示x轴网格线
            yaxis_showgrid=True,  # 显示y轴网格线
            height=400,  # 设置高度
            width=500,  # 设置宽度
        )
        st.plotly_chart(fig)

    col3, col4 = st.columns([30, 70])
    with col3:
        # 选择波长
        selected_columns = st.multiselect('(可多选波长)', df_T.columns[1:])
        st.write(f'You selected {selected_columns}')
        # 选择保存名字
        save_name = st.text_input("输入保存的名字，例如WavePlot_.png",
                                  value='WavePlot_'+filename.replace('.xlsx', '.png'))  # 【可修改】

    with col4:
        # 创建一个空的 DataFrame 用于保存数据
        wavedata_to_save = pd.DataFrame()
        # 将波长列添加到要保存的 DataFrame 中
        wavedata_to_save['Time[s]'] = time_axis

        # 绘制光谱曲线
        fig = plt.figure()
        for column in selected_columns:
            plt.plot(time_axis, df_T[column], label=str(round(column, 1)) + 'nm')
            wavedata_to_save[str(round(column, 1)) + 'nm'] = df_T[column].values  # 不用values会报错！！！

        plt.title(f'Transmittance versus time curve \n'
                  f'{curve_name}')
        plt.xlabel('Time[s]')
        plt.ylabel('transmittance')
        plt.legend(loc='upper right')  # 调整legend的位置到右侧
        fig.tight_layout()
        # 显示图形
        st.pyplot(fig)
        # 保存图形按钮
        if st.button("保存WavePlot为png格式"):
            if save_folder == '':
                st.warning("请先输入保存文件夹的绝对路径")
            else:
                fig.savefig(os.path.join(save_folder, save_name), dpi=300)
                st.success(f"图像保存在{save_folder}文件夹下")
        # 保存数据文件按钮
        if st.button("保存WavePlot数据为excel格式"):
            if save_folder == '':
                st.warning("请先输入保存文件夹的绝对路径")
            else:
                wavedata_to_save.to_excel(os.path.join(save_folder, 'Data'+save_name.replace('.png', '.xlsx')), index=False)
                st.success(f"数据保存在{save_folder}文件夹下")

def st_main():
    st.title(":rainbow:数据处理——时间序列的光谱数据分析")  # 🌈
    # 1.0 -----读入DataFrame-----
    df, curve_name, file_name = load_data()

    if df is not None:
        df_T = data_transform(df)
        # 2.0 -----绘制某个时间点的器件光谱曲线-----
        st.subheader(":clock1:绘制某个时间点的器件光谱曲线")  # 🕐
        time_axis, save_folder = time_point_plot(df, df_T, curve_name, file_name)
        # 3.0 -----绘制某个波长下的器件透过率变化曲线-----
        st.subheader(":recycle:绘制某个波长下的器件透过率变化曲线")  # ♻️
        wavelength_plot(df, df_T, time_axis, save_folder, curve_name, file_name)

    return None


if __name__ == "__main__":
    st_main()
