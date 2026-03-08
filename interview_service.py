from vector_stores import VectorStoreService
from knowledge_base import DashScopeMultiModalEmbeddings 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models import ChatTongyi
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.documents import Document
import config_data as config
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from file_history_store import get_history
import os
import json
from pathlib import Path


def print_prompt(prompt):
    print("-" * 20)
    print(prompt)
    print("-" * 20)
    return prompt

class RagService(object):
    def __init__(self):

        self.vector_service = VectorStoreService(
            embedding=DashScopeMultiModalEmbeddings(model=config.embedding_model_name)
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户的问题。参考资料{context}"),
                ("system", "并且我提供用户的对话历史记录如下: "),
                MessagesPlaceholder("history"),
                ("user", "请回答我的问题: {input}")
            ]
        )

        self.chat_model = ChatTongyi(model=config.chat_model_name)

        self.chain = self.__get_chain()
    def __get_chain(self):
        """
        获取最终的执行链
        """
        # 检索器
        retriever = self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            if not docs:
                return "无相关参考资料"
            
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段: {doc.page_content}\n 文档元数据: {doc.metadata}\n\n"

            return formatted_str
        
        def format_for_retriever(value: dict) -> str:
            return value["input"]
        
        def format_for_prompt_template(value):
            new_value = {
                "input": value["input"]["input"],
                "context": value["context"],
                "history": value["input"]["history"],
            }
            return new_value

        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_document
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template  | print_prompt| self.chat_model |StrOutputParser()
        )
        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        
        return conversation_chain
    

# 简历 
class ResumeParser():
    """
    简历解析器 - 从文本中提取关键信息 
    """
    
    def __init__(self):
        self.skills_keywords = [
           'Python', 'Java', 'Go', 'C++', 'JavaScript', 'MySQL', 'Redis',
            'Docker', 'Kubernetes', 'Linux', '机器学习', '深度学习', 'TensorFlow',
            'PyTorch', 'NLP', 'Django', 'Flask', 'Spring', 'Vue', 'React' 
        ]
    
    def parse_from_text(self, text):
        """
        从文本内容解析简历信息
        """
        lines  = text.strip().split("\n")   # 去掉多余的空行、换行
        
        info = {
            "name": "",
            "education": [],
            "experience": [],
            "skills": [],
            "projects": []   
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查技能关键词
            for skill in self.skills_keywords:
                if skill in line and skill not in info["skills"]:
                    info["skills"].append(skill)

            # 简单分类
            if "教育" in line or "学校" in line or "大学" in line:
                current_section = "education"
                info["education"].append(line)
            elif "工作" in line or "职位" in line or "公司" in line:
                current_section = "experience"
                info["experience"].append(line)
            elif "项目" in line or "项目" in line or "项目" in line:
                current_section = "projects"
                info["projects"].append(line)
            
        return info
    
    def extract_skills_from_resume(self, text):
        """提取简历中的技能"""
        skills = []
        for skill in self.skills_keywords:
            if skill in text:
                skills.append(skill)
        return skills 
    
class QuestionGenerator():
    """面试问题生成器 - 根据简历和职位生成问题"""
    
    def __init__(self, rag_service):
        self.rag_service = rag_service

    def generate(self, resume_info, job_desc, num_questions=5):
        """根据简历和职位生成个性化问题"""
        skills = resume_info.get("skills", [])
        job_type = job_desc.get("job_type", "Python开发工程师")
        
        questions = []

        # 基于技能生成技术问题
        for skill in skills:
            # 从向量数据库检索相关问题
            retrieved_docs = self._retrieve_questions(skill)
            if retrieved_docs:
                questions.append({
                    "type": "技术问题",
                    "category": skill,
                    "question": retrieved_docs[0].page_content if retrieved_docs else None
                })

        # 添加行为问题
        behavior_docs = self._retrieve_questions("行为问题")
        if behavior_docs:
            questions.append({
                "type": "行为问题",
                "category": "个人经历",
                "question": behavior_docs[0].page_content if behavior_docs else None
            })

        # 添加场景问题
        scenario_docs = self._retrieve_questions('场景问题')
        if scenario_docs:
            questions.append({
                'type': '场景问题',
                'category': '系统设计',
                'question': scenario_docs[0].page_content if scenario_docs else None
            })
        
        return questions[:num_questions]
    
    def _retrieve_questions(self, keyword):
        """从向量数据库检索相关问题"""
        try:
            retriever = self.rag_service.vector_service.get_retriever()
            docs = retriever.invoke(keyword)
            print(f"检索关键词: {keyword}, 检索到文档数: {len(docs)}")  # 调试打印
            return docs
        except Exception as e:
            print(f"检索出错: {e}")
            return []
        
class AnswerEvaluator():
    """回答评估器 - 评估面试回答质量"""
    
    def __init__(self):
        self.dimensions = {
            'technical_accuracy': 0.4,    # 技术准确性
            'completeness': 0.3,          # 回答完整性
            'clarity': 0.2,               # 表达清晰度
            'relevance': 0.1              # 问题相关性
        }
    
    def evaluate(self, question_type, question, answer):
        """评估回答质量"""
        score = {
            'technical_accuracy': self._evaluate_technical(answer),
            'completeness': self._evaluate_completeness(answer),
            'clarity': self._evaluate_clarity(answer),
            'relevance': self._evaluate_relevance(question, answer)
        }
        
        # 计算加权总分
        total_score = sum(
            score[dim] * self.dimensions[dim] 
            for dim in score
        )
        
        # 转换为5分制
        final_score = round(total_score * 5, 1)
        
        # 生成反馈建议
        feedback = self._generate_feedback(score, answer)
        
        return {
            'score': final_score,
            'breakdown': score,
            'feedback': feedback
        }
    
    def _evaluate_technical(self, answer):
        """评估技术准确性（简化版本）"""
        if not answer or len(answer) < 20:
            return 0.2
        
        technical_terms = ['例如', '比如', '因为', '所以', '通过', '使用', '实现', '方法']
        term_count = sum(1 for term in technical_terms if term in answer)
        
        return min(0.5 + term_count * 0.1, 1.0)
    
    def _evaluate_completeness(self, answer):
        """评估回答完整性"""
        if not answer:
            return 0.0
        
        length = len(answer)
        if length < 50:
            return 0.3
        elif length < 100:
            return 0.6
        elif length < 300:
            return 0.8
        else:
            return 1.0
    
    def _evaluate_clarity(self, answer):
        """评估表达清晰度"""
        if not answer:
            return 0.0
        
        clarity_indicators = ['首先', '其次', '然后', '最后', '第一', '第二', '第三']
        has_structure = any(indicator in answer for indicator in clarity_indicators)
        
        if has_structure:
            return 0.9
        elif len(answer) > 50:
            return 0.7
        else:
            return 0.5
    
    def _evaluate_relevance(self, question, answer):
        """评估回答相关性"""
        if not question or not answer:
            return 0.0
        
        # 简单关键词匹配
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        overlap = len(question_words & answer_words)
        relevance = min(overlap / max(len(question_words), 1), 1.0)
        
        return relevance
    
    def _generate_feedback(self, score, answer):
        """生成改进建议"""
        feedback = []
        
        if score['technical_accuracy'] < 0.5:
            feedback.append("建议增加技术细节，例如具体的实现方法和使用的工具")
        
        if score['completeness'] < 0.6:
            feedback.append("回答不够完整，建议从多个角度阐述这个问题")
        
        if score['clarity'] < 0.6:
            feedback.append("建议使用首先、其次、最后等结构化表达方式")
        
        if score['relevance'] < 0.5:
            feedback.append("回答有些偏离问题，建议更直接地回应面试官的问题")
        
        if not feedback:
            feedback.append("回答得很好！继续保持")
        
        return feedback
    

class InterviewService():
    """面试服务主类 - 整合所有功能"""
    
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=DashScopeMultiModalEmbeddings(model=config.embedding_model_name)
        )
        
        self.resume_parser = ResumeParser()
        self.question_generator = QuestionGenerator(self)
        self.answer_evaluator = AnswerEvaluator()
        
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个专业的AI面试官。请根据面试者的简历和职位要求进行面试。\n简历信息:{resume_info}\n职位描述:{job_desc}"),
                ("system", "面试问题参考知识库:{context}"),
                MessagesPlaceholder("history"),
                ("user", "{input}")
            ]
        )
        
        self.chat_model = ChatTongyi(model=config.chat_model_name)
        
        self.chain = self._get_chain()
    
    def _get_chain(self):
        """获取执行链"""
        retriever = self.vector_service.get_retriever()
        
        def format_document(docs):
            if not docs:
                return "无相关参考资料"
            return "\n\n".join([f"参考问题: {doc.page_content}" for doc in docs])
        
        chain = (
            {
                "input": RunnablePassthrough(),
                "context": RunnableLambda(lambda x: x.get("input", "")) | retriever | format_document
            } | RunnableLambda(lambda x: {
                "input": x["input"],
                "context": x["context"],
                "resume_info": x.get("resume_info", ""),
                "job_desc": x.get("job_desc", ""),
                "history": x.get("history", [])
            }) | self.prompt_template | self.chat_model | StrOutputParser()
        )
        
        return RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
    
    def load_resume(self, file_path):
        """加载并解析简历"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.resume_parser.parse_from_text(text)
        except Exception as e:
            return {"error": str(e)}
    
    def load_job_desc(self, file_path):
        """加载职位描述"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            job_info = {}
            lines = content.strip().split('\n')
            for line in lines:
                if '职位名称' in line:
                    job_info['job_title'] = line.split(':')[1].strip() if ':' in line else ''
                elif '职位类型' in line:
                    job_info['job_type]'] = line.split(':')[1].strip() if ':' in line else ''
                elif '职位要求' in line:
                    job_info['requirements'] = []
                elif '加分项' in line:
                    job_info['bonus'] = []
                elif line.strip() and 'job_info' in locals():
                    if 'requirements' in job_info and len(job_info.get('requirements', [])) < 10:
                        job_info.setdefault('requirements', []).append(line.strip())
                    elif 'bonus' in job_info:
                        job_info.setdefault('bonus', []).append(line.strip())
            
            return job_info
        except Exception as e:
            return {"error": str(e)}
    
    def start_interview(self, resume_info, job_desc):
        """开始面试，生成问题"""
        print("开始生成问题...")
        print("简历信息:", resume_info)
        print("职位描述:", job_desc)
        questions = self.question_generator.generate(resume_info, job_desc)

        print("生成的问题:", questions)
        return questions
    
    def evaluate_answer(self, question_type, question, answer):
        """评估回答"""
        return self.answer_evaluator.evaluate(question_type, question, answer)
    
    def chat(self, message, resume_info=None, job_desc=None, session_config=None):
        """面试过程中的对话"""
        if session_config is None:
            session_config = config.session_config
        
        invoke_data = {
            "input": message,
            "resume_info": str(resume_info) if resume_info else "",
            "job_desc": str(job_desc) if job_desc else ""
        }
        
        return self.chain.invoke(invoke_data, session_config)
    
    

if __name__ == "__main__":
    
   # 测试面试服务
    service = InterviewService()
    
    # 测试加载简历
    print("=== 测试加载简历 ===")
    # 实际使用时从文件加载
    test_resume = """
    张三
    教育背景：清华大学 计算机科学 硕士
    技能：Python, MySQL, Docker, 机器学习
    项目：电商推荐系统、分布式爬虫
    """
    resume_info = service.resume_parser.parse_from_text(test_resume)
    print(f"解析结果: {resume_info}")
    
    # 测试生成问题
    print("\n=== 测试生成问题 ===")
    job_desc = {"job_type": "Python开发工程师"}
    questions = service.start_interview(resume_info, job_desc)
    for i, q in enumerate(questions):
        print(f"问题{i+1}: {q}")