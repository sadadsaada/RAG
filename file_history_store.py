import os
import json
from typing import Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

def get_history(session_id):
    return FileChatMessageHistory(session_id, storage_path="./chat_history")

class FileChatMessageHistory(BaseChatMessageHistory):
    """
    基于本地文件存储的聊天历史记录类
    继承自 LangChain 的 BaseChatMessageHistory，实现消息的持久化存储
    """

    def __init__(self, session_id: str, storage_path: str):
        """
        初始化聊天历史记录管理器
        :param session_id: 会话唯一标识，用于区分不同用户/不同对话
        :param storage_path: 本地存储目录路径，所有会话文件都存在这个目录下
        """
        # 保存会话ID
        self.session_id = session_id
        # 保存存储目录路径
        self.storage_path = storage_path
        # 拼接出完整的文件路径：目录 + 会话ID（用会话ID作为文件名）
        self.file_path = os.path.join(self.storage_path, self.session_id)

        # 确保存储目录存在，如果不存在则自动创建，exist_ok=True 表示目录已存在也不报错
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    @property
    def messages(self) -> list[BaseMessage]:
        """
        重写 messages 属性，用于获取当前会话的所有消息
        :return: 从本地文件中加载并反序列化后的 BaseMessage 列表
        """
        # 如果文件不存在，说明还没有消息，返回空列表
        if not os.path.exists(self.file_path):
            return []

        # 打开文件，读取所有消息的字典列表
        with open(self.file_path, "r", encoding="utf-8") as f:
            messages_dict = json.load(f)

        # 使用 LangChain 提供的 messages_from_dict 把字典列表转回 BaseMessage 对象列表
        return messages_from_dict(messages_dict)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """
        添加新消息到历史记录，并同步写入本地文件
        :param messages: 要添加的消息序列（可以是 list 或 tuple）
        """
        # 先获取当前已有的所有消息，转为列表
        all_messages = list(self.messages)
        # 把新消息扩展到已有消息列表中
        all_messages.extend(messages)

        # 使用列表推导式，把所有 BaseMessage 对象转为字典格式，方便 JSON 序列化
        new_messages = [message_to_dict(message) for message in all_messages]

        # 以写入模式打开文件，把消息字典列表以 JSON 格式写入文件
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        """
        清空当前会话的所有历史消息
        """
        # 如果文件存在，直接删除文件即可清空所有消息
        if os.path.exists(self.file_path):
            os.remove(self.file_path)