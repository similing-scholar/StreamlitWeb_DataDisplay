'''
可视化IV数据分析
'''
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import os


# 1.0 -----读入DataFrame-----
@st.cache_data(experimental_allow_widgets=True)  # 缓存加载数据
def load_data():
    # 设置上传选项，Markdown语法设置加粗
    uploaded_file = st.file_uploader("上传一个包含IV曲线数据的Excel文件，通常为[**yyyymmdd-Resistance_merged.xlsx**]文件",
                                     type=["xlsx", "xls"])
    # 设置返回参数
    if uploaded_file is not None:
        return pd.read_excel(uploaded_file)
    else:
        return None


# 2.0 -----绘制所有IV曲线-----
def plot_all_curves(df):
    st.subheader(":chart_with_upwards_trend:绘制该数据列表中所有IV曲线")  # 📈
    # 获取列名，即光谱曲线的标签
    curve_labels = df.columns[1:].tolist()  # 将Index对象转换为列表
    # 添加曲线标签选择框，默认选择所有的曲线
    selected_labels = st.multiselect("通过多项选项框模式来选择需要显示的曲线，默认加载所有曲线",
                                     curve_labels, default=curve_labels)  # default输入为列表

    # 创建一个fig
    fig = go.Figure()
    for curve_label in selected_labels:
        Potential = df.iloc[:, 0]  # 提取第一列数据作为波长数据
        Current = df[curve_label]
        # 使用 Plotly 来绘制曲线
        fig.add_trace(go.Scatter(x=Potential, y=Current, mode='lines', name=curve_label))

    # 设置常用的绘图样式
    fig.update_layout(
        title='IV Curve of Films',
        title_x=0.35,  # 控制标题水平居中，默认值是0.5
        xaxis_title='Potential (V)',
        yaxis_title='Current (A)',
        xaxis_type='linear',  # 使用对数坐标，改为'log'
        yaxis_type='linear',
        yaxis_tickformat='.3e',  # 科学计数法
        xaxis_showgrid=True,  # 显示x轴网格线
        yaxis_showgrid=True,  # 显示y轴网格线
        xaxis_showline=False,  # 显示x轴线
        yaxis_showline=False  # 显示y轴线
    )
    # 模拟plt中的边框效果
    fig.add_shape(
        type="rect",
        x0=df.iloc[:, 0].min(),
        y0=min(df[selected_labels].min()),  # 所有选择曲线中的最小值
        x1=df.iloc[:, 0].max(),
        y1=max(df[selected_labels].max()),  # 所有选择曲线中的最大值
        line=dict(color="black", width=2),
        opacity=1,
        layer="below"
    )

    # 使用st.plotly_chart()显示Plotly图形
    return st.plotly_chart(fig)


# 3.0 -----绘制单独的IV曲线并保存图片和数据-----
def plot_single_curve_save_datas(df):
    st.subheader(":chart_with_upwards_trend:绘制该数据列表中单独的IV曲线")  # 📈
    # 获取列名，即光谱曲线的标签
    curve_labels = df.columns[1:].tolist()

    # 3.1 创建两列37分布局：左侧为设置区域，右侧绘制线性拟合后的曲线
    col1, col2 = st.columns([30, 70])

    with col1:
        # 选择要绘制的曲线
        selected_curve = st.selectbox("通过单项选项框模式来选择需要显示的曲线", curve_labels)
        # 获取对应IV曲线的数据
        Potential = df.iloc[:, 0]  # 提取第一列数据作为波长数据
        Current = df[selected_curve]

        # 设置线性拟合的电压范围
        voltage_range_start = st.number_input("线性拟合电压范围的起始值 (V)", min_value=min(Potential),
                                              max_value=max(Potential), value=min(Potential))
        voltage_range_end = st.number_input("线性拟合电压范围的结束值 (V)", min_value=min(Potential),
                                            max_value=max(Potential), value=max(Potential))
        # 添加曲线类型选项卡
        curve_type = st.radio("选择曲线所属类型",
                              ["欧姆型（恒电阻）", "隧穿型（出现负电阻）", "半导体型（电阻减小）"])

    # 在右侧绘制线性拟合后的曲线
    with col2:
        # 删除包含NaN值的行：电流列比电压列少的地方由NaN值填充
        non_nan_indices = Current.notna()
        Potential = Potential[non_nan_indices]
        Current = Current[non_nan_indices]
        # 在指定电压范围内进行线性拟合
        voltage_range_mask = (Potential >= voltage_range_start) & (Potential <= voltage_range_end)
        fit_potential = Potential[voltage_range_mask]
        fit_current = Current[voltage_range_mask]
        # 计算线性拟合的系数
        coeffs = np.polyfit(fit_potential, fit_current, 1)
        # 计算相关系数
        correlation = np.corrcoef(fit_potential, fit_current)[0, 1]
        fit_line = np.poly1d(coeffs)

        # 创建新的图表
        fig = plt.figure()
        plt.grid(True)  # 辅助网格样式
        # 在标题中添加相关系数,线性拟合的斜率与截距(科学计数法表示)
        title = (f'IV Curve with Linear Fit Coefficients\n'
                 f'Correlation Coefficient: {correlation:.4f}, '
                 f'Slope: {"{:.2e}".format(coeffs[0])}')
        plt.title(title)
        plt.xlabel('Potential (V)')
        plt.ylabel('Current (A)')
        # 使用科学计数法表示纵轴坐标
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # 绘制直线
        plt.plot(Potential, Current, marker='o', linestyle='-', label='IV Curve')
        plt.plot(fit_potential, fit_line(fit_potential), linestyle='--', label='Linear Fit')

        plt.legend()
        # 使用st.pyplot()显示Matplotlib图形
        st.pyplot(fig)

    # 检查session_state是否包含所需的数据，如果没有则创建存储和访问跨会话状态的数据
    if 'results_df' not in st.session_state:
        st.session_state.results_df = pd.DataFrame(
            columns=['Curve Label', 'Curve Type', 'Correlation Coefficient', 'Slope', 'Intercept',
                     'voltage_range_start (V)', 'voltage_range_end (V)'])

    # 3.2 保存目录
    save_folder_path = st.text_input("输入保存文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")

    # 3.3 保存图片为png格式
    if st.button("保存当前图片为png格式"):
        if not os.path.exists(save_folder_path):
            st.error("指定的目录不存在，请确保目录存在。")
        else:
            # 生成保存图像的路径
            save_path = os.path.join(save_folder_path, f"Resistance_{selected_curve}.png")
            # 保存图像
            fig.savefig(save_path, dpi=300)
            st.success(f"图片已保存到 {save_path}")

            # 将该图像线性拟合数据添加到DataFrame
            new_data = {'Curve Label': selected_curve, 'Curve Type': curve_type,
                        'Correlation Coefficient': correlation, 'Slope': coeffs[0], 'Intercept': coeffs[1],
                        'voltage_range_start (V)': voltage_range_start, 'voltage_range_end (V)': voltage_range_end}
            st.session_state.results_df = st.session_state.results_df.append(new_data, ignore_index=True)

    # 3.4 展示DataFrame的结果
    st.subheader(":page_with_curl:相关数据结果汇总")  # 📃
    # 格式化Slope和Intercept列为科学计数法
    st.dataframe(st.session_state.results_df.style.format({'Slope': '{:.4e}', 'Intercept': '{:.4e}'}))

    # 3.5 添加按钮以清空results_df
    if st.button("**按两下清空**当前表格中的数据"):
        st.session_state.results_df = pd.DataFrame(
            columns=['Curve Label', 'Curve Type', 'Correlation Coefficient', 'Slope', 'Intercept',
                     'voltage_range_start (V)', 'voltage_range_end (V)'])

    # 3.6 添加dataframe保存为Excel按钮
    if st.button("保存当前表格中的数据为Excel文件"):
        if not os.path.exists(save_folder_path):
            st.error("指定的目录不存在，请确保目录存在。")
        else:
            # 生成保存Excel文件的路径
            mergedfile_name = os.path.basename(save_folder_path).split('-')[0]
            excel_path = os.path.join(save_folder_path, mergedfile_name + "-LinearFit_Coefficients.xlsx")
            # 保存DataFrame为Excel文件
            st.session_state.results_df.to_excel(excel_path, index=False)
            st.success(f"结果已保存到 {excel_path}")

    return None


# 主函数
def main():
    # 设置页面宽度必须在第一句
    # st.set_page_config(layout="centered")
    st.title(":bar_chart:数据预处理——薄膜的IV曲线分析")  # 📊代码为:bar_chart:
    df = load_data()
    if df is not None:
        plot_all_curves(df)
        plot_single_curve_save_datas(df)


if __name__ == "__main__":
    main()
