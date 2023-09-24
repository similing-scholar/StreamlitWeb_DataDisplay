'''
multipage_1
'''
import streamlit as st
from pages.multipages import streamlit_IV_resistance, image_crop, image_coffee_ring


# ----------页面属性控制----------
# 设置页面宽度必须在第一句，且全局只能设置一次
st.set_page_config(layout="centered")

# 设置选项按钮，选择运行哪个数据预处理程序
tools = ['IV曲线电阻率计算', '图片裁剪', '咖啡环数据采集']
option = st.sidebar.selectbox('选择运行哪个数据预处理小程序', tools)
if option == 'IV曲线电阻率计算':
    streamlit_IV_resistance.main()
elif option == '图片裁剪':
    image_crop.main()
elif option == '咖啡环数据采集':
    image_coffee_ring.main()




