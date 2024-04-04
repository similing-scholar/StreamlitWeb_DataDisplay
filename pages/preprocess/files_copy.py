"""复制移动指定文件"""
import streamlit as st
import os
import shutil


def file_copy_with_subfolders(source_folder, target_folder, extension):
    # 遍历根目录下的所有子文件夹及文件
    for root, dirs, files in os.walk(source_folder):
        # 计算在目标文件夹中对应的子文件夹路径
        target_root = os.path.join(target_folder, os.path.relpath(root, source_folder))

        # 确保目标文件夹对应的子文件夹存在，如果不存在则创建
        if not os.path.exists(target_root):
            os.makedirs(target_root)

        # 复制文件到目标文件夹的相应位置
        for file in files:
            # 构建源文件的完整路径
            source_file = os.path.join(root, file)
            # 构建目标文件的完整路径
            target_file = os.path.join(target_root, file)
            if len(extension) == 0:
                # 复制文件
                shutil.copy2(source_file, target_file)
                st.success(f'已复制到{target_file}')
            else:
                extension_tuple = tuple(e.strip() for e in extension.split(','))
                if file.endswith(extension_tuple):
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    st.success(f'已复制到{target_file}')
    return None


def file_copy(source_folder, target_folder, extension):
    # 遍历源文件夹及其子文件夹
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            # 构建源文件的完整路径
            source_file = os.path.join(root, file)
            # 构建目标文件的完整路径
            target_file = os.path.join(target_folder, file)
            if len(extension) == 0:
                # 复制文件
                shutil.copy2(source_file, target_file)
                st.success(f'已复制到{target_file}')
            else:
                extension_tuple = tuple(e.strip() for e in extension.split(','))
                if file.endswith(extension_tuple):
                    # 复制文件
                    shutil.copy2(source_file, target_file)
                    st.success(f'已复制到{target_file}')
    return None


def parameter_configuration():
    # ---mode选择确定path---
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有文件'], index=0)
    if mode == '模式一：处理所有子文件夹内的所有文件':
        farther_folder = st.text_input("输入所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")

    # ---文件后缀名---
    extension_check = st.checkbox('是否通过文件后缀名筛选', value=True)
    if extension_check:
        extension = st.text_input('填写文件后缀名（可多写，用英文逗号隔开），例如：**.png, .jpg**')
    else:
        extension = ''

    # ---复制模式选择---
    target_folder = st.text_input("输入目标文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    subfolder_check = st.checkbox('是否在目标文件夹下创建相应的子文件夹', value=True)

    # ---按mode执行---
    if st.button('运行文件批量复制程序'):
        if subfolder_check:
            file_copy_with_subfolders(farther_folder, target_folder, extension)
        else:
            file_copy(farther_folder, target_folder, extension)

    return None


def st_main():
    st.title(":new: 数据预处理——批量复制文件")  # 🆕
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()