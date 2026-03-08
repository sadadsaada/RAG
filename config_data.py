
md5_path = "./md5.text"


# chroma
collection_name = "interview_knowledge"  # 面试知识库
persist_directory = "./chroma_db"


# spliter
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n","\n", "。", "？", "！", "；", "，", "、", "：", "（", "）", "【", "】", "《", "》", "、", "，", "。", "？", "！", "；", "，", "、", "：", "（", "）", "【", "】", "《", "》"]

max_split_char_number = 1000   # 文本分割阈值

# 
similarity_threshold = 3  # 检索返回匹配的文档数量


# model
embedding_model_name = "qwen3-vl-embedding"
chat_model_name = "MiniMax-M2.5"

session_config = {
        "configurable": {
            "session_id": "user_001"
        }
    } 

# 面试相关配置
INTERVIEW_CONFIG = {
    "max_questions": 5,   # 每次面试最多问题数
    "resume_folder": "../data/resumes", # 存储简历的文件夹
    "job_desc_folder": "../data/job_desc", # 存储职位描述的文件夹
    "questions_folder": "../data/qwestions", # 问题库文件夹
    "defalut_job_type": "Python开发工程师", # 默认职位类型
}