"""将同一文件夹内的所有IV测试数据（电阻）的Excel文件进行合并，并画图"""
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def merge_excel(folder_path, fit_check, w_l_value):
    """将同一个文件夹下的excel文件转化为一个总的excel文件"""
    # 获取文件夹内所有 Excel 文件的路径
    excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' not in f)]
    # 创建一个空 DataFrame 用于存储合并后的数据
    merged_df = pd.DataFrame()

    # 遍历所有 Excel 文件
    for excel_file in excel_files:
        file_path = os.path.join(folder_path, excel_file)

        # 读取 Excel 文件，并转化为dataframe
        workbook = pd.ExcelFile(file_path)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name，即电学曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]
        # 将电流列名重命名为sheet_name即file_name
        df.rename(columns={df.columns[1]: curve_label}, inplace=True)

        # 如果第一次读取，直接作为基础 DataFrame
        if merged_df.empty:
            merged_df = df
        else:
            # 合并 Excel 文件，共享第一列 'Potential[V]'
            merged_df = pd.merge(merged_df, df, on='Potential[V]', how='outer')
            # st.write(merged_df)

    # 将合并后的 DataFrame 写入新 Excel 文件
    output_name = os.path.basename(folder_path)
    output_path = os.path.join(folder_path, f'Resistance_merged_{output_name}.xlsx')
    merged_df.to_excel(output_path, index=False, engine='openpyxl', sheet_name='Resistance')
    st.success(f"Merged excel file saved to {output_path}")

    if fit_check:
        merge_excel_fit_line(merged_df, folder_path, w_l_value)

    return None


def merge_excel_fit_line(df_merged, folder_path, w_l_value):
    # 获取列名，即IV曲线的标签
    curve_labels = df_merged.columns[1:]
    # 创建空列表
    results_data = []
    diff_slope_data = []  # 差分
    gradient_slope_data = []  # 梯度

    for curve_label in curve_labels:
        # 获取对应IV曲线的数据
        Potential = df_merged.iloc[:, 0]  # 提取第一列数据作为波长数据
        Current = df_merged[curve_label]

        # 删除包含NaN值的行：电流列比电压列少的地方由NaN值填充
        non_nan_indices = Current.notna()
        Potential = Potential[non_nan_indices]
        Current = Current[non_nan_indices]

        # 在给定电压范围内进行线性拟合并计算相关系数
        voltage1 = Potential.iloc[0]  # 使用电流列的第一个值对应的电压
        voltage2 = Potential.iloc[-1]  # 使用电流列的最后一个值对应的电压
        voltage_range_mask = (Potential >= voltage1) & (Potential <= voltage2)
        fit_potential = Potential[voltage_range_mask]
        fit_current = Current[voltage_range_mask]
        # 计算线性拟合的系数
        coeffs = np.polyfit(fit_potential, fit_current, 1)
        # 计算相关系数
        correlation = np.corrcoef(fit_potential, fit_current)[0, 1]

        # 固定参数
        curve_type = '欧姆型（恒电阻）'
        sheet_resistance = (1 / coeffs[0]) * w_l_value  # 方阻：Rs=RW/L, W界面宽1.5 L长2.5 【注意：斜率的倒数才是电阻】

        # 计算差分斜率
        diff_slopes = np.diff(Current) / np.diff(Potential)
        diff_slope_data.append(pd.Series(diff_slopes, name=curve_label))
        mean_diff_slope = np.mean(diff_slopes)  # 均值
        cv_diff_slope = np.std(diff_slopes) / mean_diff_slope if mean_diff_slope != 0 else float('inf')  # 变异系数
        diff_sheet_resistance = (1 / mean_diff_slope) * w_l_value

        # 计算梯度斜率（一阶导数）
        gradient_slopes = np.gradient(Current, Potential)
        gradient_slope_data.append(pd.Series(gradient_slopes, name=curve_label))
        mean_gradient_slope = np.mean(gradient_slopes)
        cv_gradient_slope = np.std(gradient_slopes) / mean_gradient_slope if mean_gradient_slope != 0 else float('inf')
        gradient_sheet_resistance = (1 / mean_gradient_slope) * w_l_value

        # 将结果添加到DataFrame
        data_dict = {'Curve Label': curve_label, 'Curve Type': curve_type, 'W/L': w_l_value,
                     'voltage_range_start[V]': voltage1, 'voltage_range_end[V]': voltage2,
                     'Correlation Coefficient': correlation, 'Fit Slope': coeffs[0],
                     'Fit Intercept': coeffs[1],
                     'Fit Sheet Resistance[ohm/sq]': sheet_resistance,
                     'Mean Diff Slope': mean_diff_slope, 'CV Diff Slope': cv_diff_slope,
                     'diff_sheet_resistance': diff_sheet_resistance,
                     'Mean Deriv Slope': mean_gradient_slope, 'CV Deriv Slope': cv_gradient_slope,
                     'gradient_sheet_resistance': gradient_sheet_resistance}
        # 将当前数据添加到列表中
        results_data.append(data_dict)

    # 将列表转换为 DataFrame
    results_df = pd.DataFrame(results_data)
    diff_slope_df = pd.DataFrame(diff_slope_data).transpose()
    gradient_slope_df = pd.DataFrame(gradient_slope_data).transpose()
    # 将合并后的 DataFrame 写入新 Excel 文件
    output_name = os.path.basename(folder_path)
    output_path = os.path.join(folder_path, f'LinearFit_merged_{output_name}.xlsx')
    # results_df.to_excel(output_path, index=False, engine='openpyxl', sheet_name='LinearFit')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        results_df.to_excel(writer, index=False, sheet_name='LinearFit')
        diff_slope_df.to_excel(writer, index=True, sheet_name='DiffSlope')
        gradient_slope_df.to_excel(writer, index=True, sheet_name='DerivSlope')

    st.success(f"LinearFit excel file saved to {output_path}")
    return None


def merged_curve(folder_path):
    """所有曲线画在一个图中"""
    merged_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('Resistance_merged' in f)]
    for merged_file_name in merged_files:
        merged_file_path = os.path.join(folder_path, merged_file_name)
        # 读取excel文件数据
        df_merged = pd.read_excel(merged_file_path, engine='openpyxl', sheet_name='Resistance')
        # 获取列名，即IV曲线的标签
        curve_labels = df_merged.columns[1:]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个IV曲线并绘总图
        plt.figure()
        plt.grid(True)  # 辅助网格样式
        plt.title('IV Curve')
        plt.xlabel('Potential[V]')
        plt.ylabel('Current[A]')
        # 使用科学计数法表示纵轴坐标
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        # 自定义颜色映射的颜色列表
        custom_colors = ['#E91ECC', '#E91E99', '#FFC0CB', '#9C27B0', '#3F51B5', '#C0CBFF', '#2196F3',
                         '#00BCD4', '#009688', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107',
                         '#FF9800', '#FF5722', '#F44336', '#c82423', '#795548', '#9E9E9E', '#607D8B']
        # 创建自定义的颜色映射
        custom_cmap = ListedColormap(custom_colors)
        # 使用自定义颜色映射分配颜色给曲线
        colors = custom_cmap(np.linspace(0, 1, len(curve_labels)))

        # 循环内只进行绘图设置提高效率
        for i, curve_label in enumerate(curve_labels):
            # 获取对应IV曲线的数据
            Potential = df_merged.iloc[:, 0]  # 提取第一列数据作为波长数据
            Current = df_merged[curve_label]
            plt.plot(Potential, Current, label=curve_label, color=colors[i])

        plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1.0))  # 调整legend的位置到右侧
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, merged_file_path.replace('.xlsx', '.png')), dpi=300)
        plt.close()
        st.success(f"Merged {merged_file_name} PNG saved to {folder_path}")

    return None


def single_curve(folder_path, w_l_value):
    """单个数据画单个曲线"""
    single_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and ('merge' not in f)]
    for single_file_name in single_files:
        single_file_path = os.path.join(folder_path, single_file_name)
        # 读取excel文件数据
        workbook = pd.ExcelFile(single_file_path)
        data_sheet = workbook.sheet_names[0]
        df = workbook.parse(data_sheet)
        # 获取file_name，即电学曲线的标签
        parameter_df = workbook.parse('parameter')
        curve_label = parameter_df['File Name'][0]

        # 提前设置图形属性，避免重复
        plt.rcParams['font.sans-serif'] = ['simhei']
        plt.rcParams['axes.unicode_minus'] = False

        # 遍历每个IV曲线并绘总图
        plt.figure()
        plt.grid(True)  # 辅助网格样式
        plt.xlabel('Potential[V]')
        plt.ylabel('Current[A]')
        # 使用科学计数法表示纵轴坐标
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # 获取对应IV曲线的数据
        potential = df.iloc[:, 0]
        current = df.iloc[:, 1]
        # 计算线性拟合的系数
        coeffs = np.polyfit(potential, current, 1)
        # 计算相关系数
        correlation = np.corrcoef(potential, current)[0, 1]
        fit_line = np.poly1d(coeffs)
        # 绘制IV曲线
        plt.plot(potential, current, marker='o', linestyle='-', label=curve_label)
        plt.plot(potential, fit_line(potential), linestyle='--', label='Linear Fit')

        # 在标题中添加相关系数,线性拟合的斜率与截距(科学计数法表示)
        title = (f'IV Curve with Linear Fit Coefficients\n'
                 f'Correlation Coefficient: {correlation:.4f}, '
                 f'Slope: {coeffs[0]:.2e}\n'
                 f'Sheet Resistance[ohm/sq]: {(1 / coeffs[0]) * w_l_value:.2e}')
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(folder_path, single_file_name.replace('.xlsx', '.png')), dpi=300)
        plt.close()
        st.success(f"Single {single_file_name} PNG saved to {folder_path}")

    return None


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    st.subheader('文件合并处理')
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有excel', '模式二：处理单个文件夹下的所有excel'],
                    index=1)
    if mode == '模式一：处理所有子文件夹内的所有excel':
        excel_farther_folder = st.text_input(
            "输入excel所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有excel':
        excel_folder = st.text_input("输入excel所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")

    # ---直线拟合---
    fit_check = st.checkbox('对合并的数据进行直线拟合并保存参数', value=True)

    # ---输入w/l值---
    w_l_value = st.number_input('输入w/l值（方阻的截面宽度/长）', value=2.5 / 1.5)

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in
                          os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                merge_excel(subfolder, fit_check, w_l_value)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            merge_excel(excel_folder, fit_check, w_l_value)

    st.subheader('画图程序（可以独立使用，共用上面的路径输入项）')
    # ---绘制merged选择---
    single_fig = st.checkbox('是否绘制single_excel（一个excel文件中只有一个IV数据）', value=True)
    merged_fig = st.checkbox('是否绘制merged_excel（一个excel文件中有多个IV数据）', value=True)
    if merged_fig:
        st.warning('确保文件夹内已经通过运行**文件转换程序**顺利生成**merged_excel**')

    # ---绘图---
    if st.button('将excel数据绘制成IV曲线'):
        if mode == '模式一：处理所有子文件夹内的所有excel':
            # 获取所有子文件夹的路径
            subfolders = [os.path.join(excel_farther_folder, subfolder) for subfolder in
                          os.listdir(excel_farther_folder)]
            for subfolder in subfolders:
                if single_fig:
                    single_curve(subfolder, w_l_value)
                if merged_fig:
                    merged_curve(subfolder)
        elif mode == '模式二：处理单个文件夹下的所有excel':
            if single_fig:
                single_curve(excel_folder, w_l_value)
            if merged_fig:
                merged_curve(excel_folder)

    return None


def st_main():
    st.title(":twisted_rightwards_arrows: 数据预处理——电阻.excel数据合并与画图")  # 🔀
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
