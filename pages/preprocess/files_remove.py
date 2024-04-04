"""删除指定文件"""
import streamlit as st
import os


def file_remove(file_path):
    os.remove(file_path)
    return st.success(f'已删除{file_path}')


def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有文件', '模式二：处理单个文件夹下的所有文件'], index=1)
    if mode == '模式一：处理所有子文件夹内的所有文件':
        png_farther_folder = st.text_input("输入所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")
    elif mode == '模式二：处理单个文件夹下的所有文件':
        png_folder = st.text_input("输入所在文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")

    # ---文件后缀名---
    extension = st.text_input('填写文件后缀名，例如：**.png**')

    # ---按mode执行---
    if st.button('运行文件批量删除程序'):
        st.warning('永久删除文件，无法恢复！')
        if mode == '模式一：处理所有子文件夹内的所有文件':
            png_files = [os.path.join(root, file) for root, _, files in os.walk(png_farther_folder) for file in
                         files if file.endswith(extension)]
            st.write(png_files)
            for file_path in png_files:
                file_remove(file_path)
        elif mode == '模式二：处理单个文件夹下的所有文件':
            png_files = [os.path.join(png_folder, file) for file in os.listdir(png_folder) if file.endswith(extension)]
            for file_path in png_files:
                file_remove(file_path)

    return None


def st_main():
    st.title(":free: 数据预处理——批量删除文件")  # 🆓
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()