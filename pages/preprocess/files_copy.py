import streamlit as st
import os
import shutil


def file_copy_with_subfolders(source_folder, target_folder, extension):
    for root, dirs, files in os.walk(source_folder):
        target_root = os.path.join(target_folder, os.path.relpath(root, source_folder))

        if not os.path.exists(target_root):
            os.makedirs(target_root)

        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_root, file)
            if len(extension) == 0:
                shutil.copy2(source_file, target_file)
                st.success(f'已复制到{target_file}')
            else:
                extension_tuple = tuple(e.strip() for e in extension.split(','))
                if file.endswith(extension_tuple):
                    shutil.copy2(source_file, target_file)
                    st.success(f'已复制到{target_file}')
    return None


def file_copy(source_folder, target_folder, extension):
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_folder, file)
            if len(extension) == 0:
                shutil.copy2(source_file, target_file)
                st.success(f'已复制到{target_file}')
            else:
                extension_tuple = tuple(e.strip() for e in extension.split(','))
                if file.endswith(extension_tuple):
                    shutil.copy2(source_file, target_file)
                    st.success(f'已复制到{target_file}')
    return None


def file_copy_arithmetic_sequence(src_folder, dst_folder, start=0, step=1):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    files = sorted(os.listdir(src_folder))
    for i in range(start, len(files), step):
        src_file = os.path.join(src_folder, files[i])
        dst_file = os.path.join(dst_folder, files[i])
        shutil.copy2(src_file, dst_file)
        st.success(f'已复制到{dst_file}')
    return None


def parameter_configuration():
    mode = st.radio('选择处理模式', ['模式一：处理所有子文件夹内的所有文件', '模式二：按等差数列提取文件'], index=0)
    farther_folder = st.text_input("输入所在文件夹的上一级目录的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test**")

    extension_check = st.checkbox('是否通过文件后缀名筛选', value=True)
    if extension_check:
        extension = st.text_input('填写文件后缀名（可多写，用英文逗号隔开），例如：**.png, .jpg**')
    else:
        extension = ''

    target_folder = st.text_input("输入目标文件夹的绝对路径，例如：**C:\\Users\\JiaPeng\\Desktop\\test\\2023**")
    subfolder_check = st.checkbox('是否在目标文件夹下创建相应的子文件夹', value=True)

    if mode == '模式二：按等差数列提取文件':
        start = st.number_input('输入等差数列的起始索引', min_value=0, value=0)
        step = st.number_input('输入等差数列的步长', min_value=1, value=1)

    if st.button('运行文件批量复制程序'):
        if mode == '模式一：处理所有子文件夹内的所有文件':
            if subfolder_check:
                file_copy_with_subfolders(farther_folder, target_folder, extension)
            else:
                file_copy(farther_folder, target_folder, extension)
        elif mode == '模式二：按等差数列提取文件':
            file_copy_arithmetic_sequence(farther_folder, target_folder, start, step)

    return None


def st_main():
    st.title(":new: 数据预处理——批量复制文件")  # 🆕
    parameter_configuration()
    return None


if __name__ == '__main__':
    st_main()
