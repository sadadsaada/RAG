"""
知识库更新服务
"""

import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime
import dashscope  # 新增：导入dashscope核心库
from langchain_core.embeddings import Embeddings  # 新增：导入基础嵌入类

# 新增：自定义支持qwen3-vl-embedding的嵌入类
class DashScopeMultiModalEmbeddings(Embeddings):
    def __init__(self, model: str = "qwen3-vl-embedding", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请配置DASHSCOPE_API_KEY环境变量！")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._get_single_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._get_single_embedding(text)

    def _get_single_embedding(self, text: str) -> list[float]:
        response = dashscope.MultiModalEmbedding.call(
            api_key=self.api_key,
            model=self.model,
            input=[{"text": text}]
        )
        if response.status_code == 200:
            return response.output["embeddings"][0]["embedding"]
        else:
            raise ValueError(f"嵌入失败：{response.message}")
def check_md5(md5_str: str):
    """检查传入的md5字符串是否已经被处理过"""
    # return False(md5未处理过)True(已经处理过，已有记录)
    if not os.path.exists(config.md5_path):
        # if进入表示文件不存在  那肯定没有处理过这个md5文件
        with open(config.md5_path, "w", encoding="utf-8") as f:
            return False
    else:
        # 读取文件内容
        for line in open(config.md5_path, "r", encoding="utf-8").readlines():
            line = line.strip()  # 处理字符串前后的空格和回车
            if line == md5_str:
                return True  # 已处理过
        return False
            


def save_md5(md5_str: str):
    """将传入的md5字符串记录到文件内保存"""
    with open(config.md5_path, "a", encoding="utf-8") as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str: str, encoding="utf-8"):
    """将传入的字符串转换为md5字符串"""
    # 将字符串转换为bytes字节数组
    str_bytes = input_str.encode(encoding=encoding)
    
    # 创建md5对象
    md5_obj = hashlib.md5()         # 得到md5对象
    md5_obj.update(str_bytes)       # 更新内容（传入即将计算的字符串）
    md5_hex = md5_obj.hexdigest()   # 得到md5的十六进制字符串

    return md5_hex




class knowledgeBaseService(object):

    def __init__(self):
        # 创建数据库文件夹  不存在则创建   创建成功返回True
        os.makedirs(config.persist_directory, exist_ok=True)
        # 先初始化自定义嵌入类
        self.embedding = DashScopeMultiModalEmbeddings(model="qwen3-vl-embedding")
        self.chroma =  Chroma(          # 向量存储的实例chroma向量库对象
            collection_name=config.collection_name,    # 数据库的表名
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,    # 数据库本地存储文件夹
        )     
        self.spliter = RecursiveCharacterTextSplitter(# 文本分割的对象
            chunk_size=config.chunk_size,   # 分割后的文本段大小
            chunk_overlap=config.chunk_overlap,   # 分割后的文本段重叠大小
            separators=config.separators,   # 分割符
            length_function=len,   # 计算文本长度的函数
        )
          

    def upload_by_str(self, data: str, filename):
        """将传入的字符串进行向量化  存入向量数据库中"""
        # 先得到传入字符串的md5值
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "【跳过】内容已存在，无需重复向量化！"
        
        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小史",
        }
  
        self.chroma.add_texts(   # 内容就加载到向量库中
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        save_md5(md5_hex)

        return "【成功】内容已成功存入向量库！"

if __name__ == "__main__":
    service = knowledgeBaseService()
    r = service.upload_by_str("你好，我是小史，我是一个学生", "test.txt")
    print(r)