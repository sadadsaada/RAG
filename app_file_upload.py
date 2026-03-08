# app_file_upload.py：知识库更新主程序 (streamlit)
# 基于streamlit完成WEB页面的开发

# Streamlit:当WEB页面元素发生变化:则代码重新执行一遍
import streamlit as st
# from knowledge_base import knowledgeBaseService
from knowledge_base import knowledgeBaseService
import time

# 添加网页标题
st.title("知识库更新服务")

# file_uploader文件上传组件
uploader_file = st.file_uploader(
    label="请在下方上传知识库文件",
    type=["txt","pdf","docx","md"],
    accept_multiple_files = False,
)
# session_state是一个字典
if "service" not in st.session_state:
    st.session_state["service"] = knowledgeBaseService()


if uploader_file is not None:
    # 文件信息
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024  # KB
    
    # 打印文件信息
    st.subheader(f"文件名: {file_name}")
    st.write(f"文件格式:{file_type} | 大小: {file_size:.2f} KB")

    # 提取、显示文件内容
    file_content = uploader_file.getvalue().decode("utf-8")
    st.write(file_content)

    text = uploader_file.getvalue().decode("utf-8")

    with st.spinner("正在载入知识库..."):
        # 调用知识库服务
        # result = st.session_state["service"].upload_by_str(text, file_name)
        time.sleep(1)
        result = st.session_state["service"].upload_by_str(text, file_name)
        st.write(result)