"""
page_1：数据处理，从获取的标准格式数据中，进一步提取有用信息处理
"""
import streamlit as st

from pages.process import (time_series_Spectrum, time_series_CV, IV_resistance, image_crop, image_coffee_ring,
                           confocal_heatmap, electropolymerization_analysis)

# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="centered")

# 设置选项按钮，选择运行哪个数据处理程序
tools = ['IV曲线电阻率计算', '图片裁剪', '咖啡环数据采集', '时间序列的光谱数据', '时间序列的电学数据', '激光共聚焦数据', '电聚合I-t曲线分析']
option = st.sidebar.selectbox('选择运行哪个数据**可视化处理**小程序', tools)
if option == 'IV曲线电阻率计算':
    IV_resistance.st_main()
elif option == '图片裁剪':
    image_crop.st_main()
elif option == '咖啡环数据采集':
    image_coffee_ring.st_main()
elif option == '时间序列的光谱数据':
    time_series_Spectrum.st_main()
elif option == '时间序列的电学数据':
    time_series_CV.st_main()
elif option == '激光共聚焦数据':
    confocal_heatmap.st_main()
elif option == '电聚合I-t曲线分析':
    electropolymerization_analysis.st_main()



