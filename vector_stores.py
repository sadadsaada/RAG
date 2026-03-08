from langchain_chroma import Chroma
import config_data as config
from knowledge_base import DashScopeMultiModalEmbeddings


class VectorStoreService(object):
    def __init__(self, embedding):
        """
        :param embedding: 嵌入模型的传入
        """
        self.embedding = embedding
        
        self.vector_store = Chroma(
            collection_name = config.collection_name,   # 指定要操作的集合名称
            embedding_function = self.embedding,   # 指定要使用的嵌入模型
            persist_directory = config.persist_directory,   # 指定要持久化的目录
        )

    def get_retriever(self):
        # 返回向量检索器，方便加入chain
        return self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})
    
if __name__ == "__main__":
    retriever = VectorStoreService(DashScopeMultiModalEmbeddings(model="qwen3-vl-embedding")).get_retriever()
    
    res = retriever.invoke("简历面试")
    print(res)