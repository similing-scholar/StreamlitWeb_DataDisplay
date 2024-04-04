"""共聚焦的excel数据，可视化分析与画图"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go


@st.cache_data(experimental_allow_widgets=True)
def load_data():
    uploaded_file = st.file_uploader("上传激光共聚焦的数据Excel文件，通常为[**Confocal_yyyymmdd-.xlsx**]文件",
                                     type=["xlsx", "xls"])
    if uploaded_file is not None:
        # 读取 Excel 文件，获取sheet_name，并转化为dataframe
        workbook = pd.ExcelFile(uploaded_file)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name
        parameter_df = workbook.parse('parameter')
        file_name = parameter_df['File Name'][0]
        return df, file_name
    else:
        return None, None


def heatmap_plot(df, file_name):
    fig = plt.figure()
    plt.imshow(df, cmap='viridis', interpolation='nearest')
    plt.colorbar()
    plt.title(file_name)
    plt.tight_layout()
    # 显示图形
    st.pyplot(fig)
    return None


def surface_plot(df, file_name):
    fig = go.Figure(data=[go.Surface(z=df.values)])
    fig.update_layout(title=file_name)
    # 显示图形
    st.plotly_chart(fig)
    return None


def st_main():
    st.title(":dart:数据处理——时间序列的电学数据分析")  # 🎯
    # 1.0 -----读入DataFrame-----
    df, file_name = load_data()

    if df is not None:
        # 2.0 -----绘制某个时间点的器件光谱曲线-----
        st.subheader(":high_brightness:绘制热力图")  #
        heatmap_plot(df, file_name)
        st.subheader(":low_brightness:绘制3D表面图")  #
        surface_plot(df, file_name)

    return None


if __name__ == "__main__":
    st_main()
