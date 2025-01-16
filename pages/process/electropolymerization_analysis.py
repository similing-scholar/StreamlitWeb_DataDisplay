"""分析电化学聚合的It曲线"""
import pandas as pd
import re
import streamlit as st
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress


# 定义读取数据并提取时间和电流的函数
def load_data(file_path, sheet_name='It'):
    try:
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        time = data['Time[s]'].values
        current = data['Current[A]'].values
        return data, time, current
    except Exception as e:
        st.error(f"读取Excel文件失败: {e}")


# 去除重复电流值
def remove_duplicates(data, time, current):
    df_unique = data[(data['Current[A]'].diff() != 0) | (data['Time[s]'] == data['Time[s]'].iloc[0])]
    time_unique = df_unique['Time[s]'].values
    current_unique = df_unique['Current[A]'].values
    return time_unique, current_unique


# 找到峰值电流和对应时间
def find_peak(current, time):
    potential_peaks = []
    for i in range(1, len(current) - 1):
        if (current[i] - current[i - 1]) > 0 and (current[i + 1] - current[i]) < 0:
            potential_peaks.append(i)

    if len(potential_peaks) > 0:
        peak_index = max(potential_peaks, key=lambda i: current[i])
        Im = current[peak_index]
        tm = time[peak_index]
        return Im, tm
    else:
        st.error("未找到任何峰值，请检查数据")
        st.warning("将返回全局最大值作为峰值")
        # 如果没有找到峰值，返回全局最大值
        global_max_index = np.argmax(current)  # 使用 numpy.argmax 找到最大值的索引
        Im = current[global_max_index]
        tm = time[global_max_index]
        return Im, tm


# 归一化时间和电流
def normalize_data(time, current, tm, Im):
    t_normalized = time / tm
    I_normalized = current / Im
    return t_normalized, I_normalized


# 定义模型公式
def model_3DI(t_normalized):
    return ((1.954 / t_normalized) ** 0.5) * (1 - np.exp(-1.2564 * t_normalized))


def model_3DP(t_normalized):
    return ((1.2254 / t_normalized) ** 0.5) * (1 - np.exp(-2.3367 * (t_normalized ** 2)))


def model_2DI(t_normalized):
    return t_normalized * np.exp(0.5 * (1 - t_normalized ** 2))


def model_2DP(t_normalized):
    return (t_normalized ** 2) * np.exp(2 / 3 * (1 - t_normalized ** 3))


# 计算电荷量
def calculate_charge(time, current):
    charge = np.zeros(len(time))
    for i in range(1, len(time)):
        charge[i] = charge[i - 1] + current[i - 1] * (time[i] - time[i - 1])
    return charge


# 计算 ln(-ln(1 - y(t))) 并进行线性拟合
def fit_ln_term(charge_normalized, time, tm):
    y_t = charge_normalized
    # 计算 1 - y(t) 并避免 1 - y(t) <= 0
    mask_valid = (y_t < 1) & (y_t > 0)  # y_t 必须在 0 和 1 之间
    y_t_valid = y_t[mask_valid]
    time_valid = time[mask_valid]

    # 检查是否有足够的有效数据
    if len(y_t_valid) == 0:
        st.error("没有有效的 y(t) 数据点 (0 < y(t) < 1)")

    # 计算 ln(-ln(1 - y(t)))
    try:
        ln_term = np.log(-np.log(1 - y_t_valid))
    except Exception as e:
        st.error(f"计算 ln(-ln(1 - y(t))) 失败: {e}")

    # 进一步筛选时间区域，假设从 t=1 秒到 t=tm 之间是线性区域
    mask_linear = (time_valid > 1) & (time_valid < tm)
    t_linear = np.log(time_valid[mask_linear])
    ln_term_linear = ln_term[mask_linear]

    # 如果数据点过少，尝试扩大时间区间
    if len(t_linear) < 2:
        st.warning("数据点太少，自动调整时间区间。")
        mask_linear = (time_valid > 1) & (time_valid < 10)  #  !!!有问题还
        t_linear = np.log(time_valid[mask_linear])
        ln_term_linear = ln_term[mask_linear]

    # 如果调整后仍然数据点太少，给出警告
    if len(t_linear) < 2:
        st.error("仍然没有足够的数据进行拟合，请调整区间或检查数据质量。")

    # 线性拟合
    slope, intercept, r_value, p_value, std_err = linregress(t_linear, ln_term_linear)
    return ln_term, slope, intercept, t_linear, ln_term_linear, time_valid


# 保存数据到 Excel
def save_to_excel(output_file_path, Im, tm, t_normalized, I_normalized, charge, charge_normalized, ln_term, t_linear,
                  ln_term_linear, slope, intercept, time_valid, time):
    try:
        with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
            # 保存峰值电流和时间
            df_peak = pd.DataFrame({'Im (A)': [Im], 'tm (s)': [tm]})
            df_peak.to_excel(writer, sheet_name='Im_value', index=False)

            # 保存图2的数据
            df2 = pd.DataFrame({'t/tm': t_normalized, 'I/Im': I_normalized})
            df2.to_excel(writer, sheet_name='Im_curve', index=False)

            # 保存图3的数据
            df3 = pd.DataFrame({'Time(s)': time, 'Charge(C)': charge})
            df3.to_excel(writer, sheet_name='Ct', index=False)

            # 保存图4的数据
            df4_all = pd.DataFrame({
                'ln(t)': np.log(time_valid),
                'ln(-ln(1 - y(t)))': ln_term
            })
            df4_all.to_excel(writer, sheet_name='Avrami', startrow=0, index=False)

            # 然后在 Sheet4 中的不同列保存拟合曲线数据
            df4_fit = pd.DataFrame({
                'ln(t)_fitted': t_linear,
                'Fitted ln(-ln(1 - y(t)))': slope * t_linear + intercept
            })
            # 在 Sheet4 中的不同列存储拟合数据
            df4_fit.to_excel(writer, sheet_name='Avrami', startrow=0, startcol=2, index=False)  # startcol=2 表示从第3列开始

    except Exception as e:
        st.error(f"保存到{output_file_path}Excel失败: {e}")


# 绘图并保存图片
def plot_and_save(time, current, t_normalized, I_normalized, Im, tm,
                  charge, ln_term, t_linear, ln_term_linear, slope, intercept, I_3DI, I_3DP,
                 I_2DI, I_2DP, t_fit, save_path, time_valid):
    try:
        plt.figure(figsize=(12, 10))

        # 图1: 电流随时间变化
        plt.subplot(2, 2, 1)
        plt.plot(time, current, label=f'tm{tm:.4f}s,Im{Im:.4f}A', color='blue')
        plt.xlabel('时间 (s)', fontsize=12)
        plt.ylabel('电流 (A)', fontsize=12)
        plt.title('电流随时间变化', fontsize=14)
        plt.legend()
        plt.grid(True)

        # 图2: 归一化电流与时间及模型拟合
        plt.subplot(2, 2, 2)
        plt.scatter(t_normalized, I_normalized, label='实验数据', color='black', s=2)
        plt.plot(t_fit, I_3DI, label='3DI 模型', linestyle='-', color='blue')
        plt.plot(t_fit, I_3DP, label='3DP 模型', linestyle='--', color='cyan')
        plt.plot(t_fit, I_2DI, label='2DI 模型', linestyle='-.', color='green')
        plt.plot(t_fit, I_2DP, label='2DP 模型', linestyle=':', color='red')
        plt.xlabel('无量纲时间 (t/tm)', fontsize=12)
        plt.ylabel('无量纲电流 (I/Im)', fontsize=12)
        plt.xlim(0, 5)
        plt.ylim(0, 1.3)
        plt.title('归一化电流与时间及模型拟合', fontsize=14)
        plt.legend()
        plt.grid(True)

        # 图3: 电荷量随时间变化
        plt.subplot(2, 2, 3)
        plt.plot(time, charge, label='电荷随时间变化', color='blue')
        plt.xlabel('时间 (s)', fontsize=12)
        plt.ylabel('电荷量 (C)', fontsize=12)
        plt.title('电荷量随时间变化', fontsize=14)
        plt.legend()
        plt.grid(True)

        # 图4: ln(-ln(1 - y(t))) vs ln(t) 及线性拟合
        plt.subplot(2, 2, 4)

        # 绘制所有有效数据点
        plt.scatter(np.log(time_valid), ln_term, label='所有数据点', color='lightgray', s=2)

        # 绘制拟合区域的数据点
        plt.scatter(t_linear, ln_term_linear, label='拟合数据点', color='purple', s=2)

        # 绘制拟合线
        plt.plot(t_linear, slope * t_linear + intercept, label=f'线性拟合: y={slope:.4f}x + {intercept:.4f}',
                 linestyle='--', color='red')

        plt.xlabel('ln(t)', fontsize=12)
        plt.ylabel('ln(-ln(1 - y(t)))', fontsize=12)
        plt.title('ln(-ln(1 - y(t))) vs ln(t)及线性拟合', fontsize=14)
        plt.legend()
        plt.grid(True)

        # 设置支持中文的字体
        plt.rcParams['font.family'] = 'SimHei'  # 设置字体为黑体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示问题
        plt.tight_layout()

        # 保存图像
        plt.savefig(save_path)
        plt.close()
    except Exception as e:
        st.error(f"绘图失败: {e}")

def It_analysis(file_path):
    # 读取数据
    try:
        data, time, current = load_data(file_path)
    except ValueError as e:
        print(e)
        return

    # 去除重复数据
    time_unique, current_unique = remove_duplicates(data, time, current)

    # 查找峰值电流和时间
    try:
        Im, tm = find_peak(current_unique, time_unique)
    except ValueError as e:
        print(e)
        return
    print(f"峰值电流 (Im): {Im:.6e} A")
    print(f"对应时间 (tm): {tm:.6f} s")

    # 归一化数据
    t_normalized, I_normalized = normalize_data(time, current, tm, Im)

    # 生成拟合的无量纲时间数据
    t_fit = np.linspace(0.01, 5, 500)

    # 计算模型曲线
    I_3DI = model_3DI(t_fit)
    I_3DP = model_3DP(t_fit)
    I_2DI = model_2DI(t_fit)
    I_2DP = model_2DP(t_fit)

    # 计算电荷量
    charge = calculate_charge(time, current)

    # 电荷量归一化
    charge_min = np.min(charge)
    charge_max = np.max(charge)
    if charge_max - charge_min == 0:
        print("电荷量归一化时分母为零，无法归一化。")
        return
    charge_normalized = (charge - charge_min) / (charge_max - charge_min)

    # 计算 ln(-ln(1 - y(t))) 并进行线性拟合
    try:
        ln_term, slope, intercept, t_linear, ln_term_linear, time_valid = fit_ln_term(charge_normalized, time, tm)
    except ValueError as e:
        print(f"线性拟合出错: {e}")
        return

    # 保存数据到 Excel
    try:
        output_excel = file_path.replace('.xlsx', '_analysis.xlsx')
        save_to_excel(output_excel, Im, tm, t_normalized, I_normalized, charge, charge_normalized, ln_term, t_linear,
                      ln_term_linear, slope, intercept, time_valid, time)
    except ValueError as e:
        print(e)
        return

    # 绘图并保存
    try:
        output_plot = file_path.replace('.xlsx', '_analysis_plot.png')
        plot_and_save(
            time=time,
            current=current,
            t_normalized=t_normalized,
            I_normalized=I_normalized,
            Im = Im,
            tm = tm,
            charge=charge,
            ln_term=ln_term,
            t_linear=t_linear,
            ln_term_linear=ln_term_linear,
            slope=slope,
            intercept=intercept,
            I_3DI=I_3DI,
            I_3DP=I_3DP,
            I_2DI=I_2DI,
            I_2DP=I_2DP,
            t_fit=t_fit,
            save_path=output_plot,
            time_valid=time_valid
        )
    except ValueError as e:
        print(e)
        return

    st.success(f"数据已保存至 {output_excel}")
    st.success(f"图像已保存至 {output_plot}")


@st.cache_data(experimental_allow_widgets=True)
def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式',
                    ['模式一：处理所有子文件夹内的所有xlsx',
                     '模式二：处理单个文件夹下的所有xlsx',
                     '模式三：处理单个xlsx'],
                    index=1)

    if mode == '模式一：处理所有子文件夹内的所有xlsx':
        xlsx_farther_folder = st.text_input(
            "输入xlsx所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**"
        )
    elif mode == '模式二：处理单个文件夹下的所有xlsx':
        xlsx_folder = st.text_input(
            "输入xlsx所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**"
        )
    elif mode == '模式三：处理单个xlsx':
        xlsx_path = st.text_input(
            "输入xlsx的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023\\It_kei.xlsx**"
        )

    # ---按mode执行---
    if st.button('运行文件转换程序'):
        if mode == '模式一：处理所有子文件夹内的所有xlsx':
            if not xlsx_farther_folder:
                st.error("请提供xlsx所在文件夹的上一级目录路径。")
            else:
                # 仅选择文件名包含 'It' 的 .xlsx 文件
                xlsx_files = [
                    os.path.join(root, file)
                    for root, _, files in os.walk(xlsx_farther_folder)
                    for file in files
                    if file.endswith('.xlsx') and 'It' in file
                ]
                if not xlsx_files:
                    st.warning("在指定目录及其子目录中未找到包含 'It' 的xlsx文件。")
                else:
                    for file_path in xlsx_files:
                        It_analysis(file_path)
                    st.success("所有文件处理完成。")

        elif mode == '模式二：处理单个文件夹下的所有xlsx':
            if not xlsx_folder:
                st.error("请提供xlsx所在文件夹的绝对路径。")
            else:
                # 仅选择文件名包含 'It' 的 .xlsx 文件
                xlsx_files = [
                    os.path.join(xlsx_folder, file)
                    for file in os.listdir(xlsx_folder)
                    if file.endswith('.xlsx') and 'It' in file
                ]
                if not xlsx_files:
                    st.warning("在指定文件夹中未找到包含 'It' 的xlsx文件。")
                else:
                    for file_path in xlsx_files:
                        It_analysis(file_path)
                    st.success("所有文件处理完成。")

        elif mode == '模式三：处理单个xlsx':
            if not xlsx_path:
                st.error("请提供要处理的xlsx文件的绝对路径。")
            else:
                filename = os.path.basename(xlsx_path)
                if 'It' not in filename:
                    st.warning("文件名不包含 'It'，将不会被处理。")
                elif not xlsx_path.endswith('.xlsx'):
                    st.warning("文件不是xlsx格式，无法处理。")
                else:
                    It_analysis(xlsx_path)
                    st.success("文件处理完成。")

    return None


def st_main():
    st.title(":repeat_one: 数据处理——电聚合It.xlsx文件分析")  # 🔂
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()

