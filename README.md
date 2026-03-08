
# 🤖 AI智能面试助手系统

基于RAG（检索增强生成）技术的智能面试助手，可实现简历智能解析、个性化面试问题生成、回答质量评估等功能。

## 🚀 项目简介

本项目是一个AI驱动的面试辅助系统，通过结合大语言模型和向量检索技术，为用户提供模拟面试体验。系统能够：

- 📄 **智能简历解析**：自动提取简历中的关键信息（技能、项目经验、教育背景）
- 🎯 **个性化问题生成**：根据求职者的简历和目标岗位生成针对性的面试问题
- 📊 **回答质量评估**：从技术准确性、完整性、清晰度、相关性等多维度评估回答质量
- 💬 **多轮对话交互**：支持与AI面试官进行持续对话互动

## 🛠️ 技术栈
- **语言**：Python
- **后端框架**：LangChain
- **向量数据库**：Chroma
- **大语言模型**：通义千问（Qwen）
- **嵌入模型**：Qwen3-VL-Embedding
- **前端界面**：Streamlit
- **会话记忆**：Session管理

## 📁 项目结构

```
.
├── app_interview.py          # 面试系统主界面（Streamlit）
├── interview_service.py      # 核心面试服务（简历解析、问题生成、回答评估）
├── vector_stores.py         # 向量存储服务
├── knowledge_base.py         # 知识库构建服务
├── config_data.py           # 配置文件
├── file_history_store.py    # 会话历史存储
├── build_knowledge_base.py # 知识库构建脚本
│
├── data/
│   ├── resumes/             # 测试简历数据
│   ├── questions/           # 面试问题知识库
│   │   ├── 技术问题_python.txt
│   │   ├── 技术问题_mysql.txt
│   │   ├── 行为问题.txt
│   │   └── 场景问题.txt
│   └── job_desc/            # 职位描述模板
│       ├── python开发工程师.txt
│       └── 算法工程师.txt
│
└── chroma_db/               # 向量数据库存储
```

## 🏃 快速开始

### 1. 安装依赖

```bash
pip install streamlit langchain langchain-community langchain-chroma dashscope
```

### 2. 构建知识库

```bash
python build_knowledge_base.py
```

### 3. 启动面试系统

```bash
streamlit run app_interview.py
```

### 4. 使用流程

1. 在左侧边栏粘贴简历内容或上传简历文件
2. 点击"解析简历"按钮，系统会自动提取技能和项目经验
3. 选择目标岗位类型
4. 点击"开始面试"生成个性化面试问题
5. 依次回答AI面试官提出的问题
6. 提交回答后获取评估反馈和改进建议
7. 面试结束后查看综合评分和历史评估记录

## ⚙️ 核心模块说明

| 文件 | 功能描述 |
|------|----------|
| `interview_service.py` | 核心服务类：ResumeParser（简历解析）、QuestionGenerator（问题生成）、AnswerEvaluator（回答评估）、InterviewService（主服务） |
| `app_interview.py` | Streamlit Web界面，包含简历上传、问题展示、回答评估、可视化展示 |
| `vector_stores.py` | Chroma向量数据库封装，支持语义检索 |
| `config_data.py` | 模型配置、知识库路径、会话参数 |

## 📊 评估维度

系统从以下四个维度评估面试回答：

- **技术准确性 (40%)**：回答中技术概念的准确性
- **回答完整性 (30%)**：是否全面覆盖问题要点
- **表达清晰度 (20%)**：逻辑结构、条理性
- **问题相关性 (10%)**：回答是否切中问题核心

## 🔧 扩展知识库

### 添加更多面试问题

在 `data/questions/` 目录下创建新的问题文件：

```txt
# data/questions/技术问题_java.txt
什么是Java中的泛型？请举例说明。
解释一下Java的反射机制及其应用场景。
Java中的线程池有哪些？请详细说明。
```

### 添加职位描述

在 `data/job_desc/` 目录下添加职位模板：

```txt
# data/job_desc/前端开发工程师.txt
职位名称：前端开发工程师
职位类型：前端
职位要求：
1. 3年以上前端开发经验
2. 熟悉Vue或React框架
3. 掌握TypeScript
加分项：
1. 有小程序开发经验
2. 了解性能优化
```

## 📝 数据样本

- **简历数据**：50份不同岗位（Python开发、算法工程、前端、数据分析、产品经理等）的测试简历
- **面试问题**：涵盖技术问题、行为问题、场景设计问题
- **职位描述**：包含常见互联网岗位的职位要求

## 🔐 环境变量

需要在环境变量中配置通义千问API Key：

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

或创建 `.env` 文件：

```
DASHSCOPE_API_KEY=your-api-key
```

## 📋 版本记录

- **v1.0** - 初始版本：基础RAG问答系统
- **v2.0** - AI面试助手：新增简历解析、问题生成、回答评估功能

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**made with ❤️ for AI interview preparation**
