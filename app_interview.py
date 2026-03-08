import streamlit as st
import time
import PyPDF2
from io import BytesIO
from interview_service import InterviewService
import config_data as config

# 页面配置
st.set_page_config(
    page_title="AI面试助手", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全新的现代化CSS设计 - 高对比度、清晰字体
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 深色主题背景 */
.stApp {
    background-color: #0f1117;
    color: #e4e6eb;
}

/* 侧边栏深色背景 */
[data-testid="stSidebar"] {
    background-color: #161b22 !important;
    border-right: 1px solid #30363d;
}

/* 侧边栏文字颜色 */
[data-testid="stSidebar"] * {
    color: #e4e6eb !important;
}

/* 主标题 - 高对比度 */
h1, h2, h3, h4, h5, h6 {
    color: #f0f6fc !important;
    font-weight: 600 !important;
    letter-spacing: -0.5px;
}

/* 卡片样式 - 玻璃拟态效果 */
.glass-card {
    background: rgba(22, 27, 34, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

/* 输入框样式 - 高对比度 */
.stTextArea textarea, .stTextInput input {
    background-color: #21262d !important;
    color: #f0f6fc !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1) !important;
}

/* 按钮样式 - 渐变效果 */
.stButton>button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 0.75rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px -1px rgba(35, 134, 54, 0.3) !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 15px -3px rgba(35, 134, 54, 0.4) !important;
}

/* 次要按钮 */
.stButton>button[kind="secondary"] {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    box-shadow: none !important;
}

.stButton>button[kind="secondary"]:hover {
    background: #30363d !important;
    border-color: #8b949e !important;
}

/* 聊天消息样式 */
.stChatMessage {
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* AI消息气泡 */
[data-testid="stChatMessage"][data-testid*="assistant"] {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: white !important;
    border-radius: 16px 16px 16px 4px !important;
    padding: 16px 20px !important;
    margin: 8px 0 !important;
    box-shadow: 0 4px 6px -1px rgba(31, 111, 235, 0.3) !important;
}

/* 用户消息气泡 */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: #21262d !important;
    color: #f0f6fc !important;
    border: 1px solid #30363d !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 16px 20px !important;
    margin: 8px 0 !important;
}

/* 进度条 */
.stProgress > div > div {
    background: linear-gradient(90deg, #238636 0%, #3fb950 100%) !important;
    border-radius: 10px !important;
}

/* 标签和说明文字 */
.stMarkdown p, .stMarkdown span {
    color: #8b949e;
    font-size: 14px;
    line-height: 1.6;
}

/* 成功消息 */
.stSuccess {
    background-color: rgba(35, 134, 54, 0.15) !important;
    border: 1px solid #238636 !important;
    color: #3fb950 !important;
    border-radius: 10px !important;
}

/* 警告消息 */
.stWarning {
    background-color: rgba(210, 153, 34, 0.15) !important;
    border: 1px solid #d29922 !important;
    color: #e3b341 !important;
    border-radius: 10px !important;
}

/* 错误消息 */
.stError {
    background-color: rgba(248, 81, 73, 0.15) !important;
    border: 1px solid #f85149 !important;
    color: #ff7b72 !important;
    border-radius: 10px !important;
}

/* 下拉选择框 */
.stSelectbox > div > div {
    background-color: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #f0f6fc !important;
}

/* 折叠面板 */
.stExpander {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
}

/* 评分显示 */
.score-badge {
    background: linear-gradient(135deg, #8957e5 0%, #a371f7 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
    display: inline-block;
}

/* 问题卡片 */
.question-card {
    background: linear-gradient(135deg, rgba(56, 139, 253, 0.1) 0%, rgba(31, 111, 235, 0.05) 100%);
    border-left: 4px solid #58a6ff;
    padding: 20px;
    border-radius: 0 12px 12px 0;
    margin: 16px 0;
}

/* 历史评估项 */
.history-item {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    transition: all 0.2s;
}

.history-item:hover {
    border-color: #58a6ff;
    transform: translateX(4px);
}

/* 分隔线 */
hr {
    border-color: #30363d !important;
    margin: 24px 0 !important;
}

/* 滚动条美化 */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0f1117;
}

::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #484f58;
}

/* 文件上传区域 */
.stFileUploader {
    background: #161b22 !important;
    border: 2px dashed #30363d !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

.stFileUploader:hover {
    border-color: #58a6ff !important;
    background: rgba(88, 166, 255, 0.05) !important;
}

/* Tab样式 */
.stTabs [data-baseweb="tab-list"] {
    background-color: #161b22 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #8b949e !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
}

.stTabs [aria-selected="true"] {
    background-color: #21262d !important;
    color: #f0f6fc !important;
    font-weight: 600 !important;
}

/* 确保所有文字清晰可读 */
p, span, label, div {
    color: #c9d1d9;
}

strong, b {
    color: #f0f6fc;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "interview_service" not in st.session_state:
    st.session_state["interview_service"] = InterviewService()

if "resume_info" not in st.session_state:
    st.session_state["resume_info"] = None

if "job_desc" not in st.session_state:
    st.session_state["job_desc"] = None

if "questions" not in st.session_state:
    st.session_state["questions"] = []

if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0

if "evaluations" not in st.session_state:
    st.session_state["evaluations"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "你好！我是AI面试官。请先上传简历和选择职位，然后我们开始模拟面试。"}
    ]

# 关键修复：使用 session_state 管理输入框的值
if "answer_input" not in st.session_state:
    st.session_state["answer_input"] = ""

# 关键修复：用于强制刷新输入框的key计数器
if "input_key_counter" not in st.session_state:
    st.session_state["input_key_counter"] = 0

# 侧边栏
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 24px;'>🎯 面试准备</h2>", unsafe_allow_html=True)
    
    # 简历上传区域
    st.markdown("<div style='background: #21262d; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top: 0;'>📄 简历上传</h4>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 文本输入", "📑 PDF上传"])
    
    with tab1:
        resume_text = st.text_area(
            "简历内容",
            height=200,
            placeholder="粘贴你的简历内容...\n例如：\n• 教育背景：XX大学 计算机科学 本科\n• 技能：Python, JavaScript, React\n• 项目经验：...",
            key="resume_text",
            label_visibility="collapsed"
        )
    
    with tab2:
        uploaded_file = st.file_uploader(
            "选择PDF文件",
            type=["pdf"],
            help="支持最大10MB的PDF文件"
        )
        
        if uploaded_file is not None:
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
                resume_text = pdf_text
                st.success("✅ PDF解析成功！内容已填充到文本框")
            except Exception as e:
                st.error(f"❌ 解析失败：{str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 解析按钮
    if st.button("🔍 智能解析简历", type="primary", use_container_width=True):
        if resume_text:
            with st.spinner("🧠 AI正在分析简历..."):
                resume_info = st.session_state["interview_service"].resume_parser.parse_from_text(resume_text)
                st.session_state["resume_info"] = resume_info
            
            st.success("✅ 解析完成！")
            with st.expander("📊 查看解析结果"):
                st.write(f"**技能栈：** {', '.join(resume_info.get('skills', ['未识别']))}")
                st.write(f"**学历：** {', '.join(resume_info.get('education', ['未识别']))[:80]}...")
                st.write(f"**经验：** {', '.join(resume_info.get('experience', ['未识别']))[:80]}...")
        else:
            st.warning("⚠️ 请先输入简历内容")
    
    st.markdown("<hr style='margin: 24px 0; border-color: #30363d;'>", unsafe_allow_html=True)
    
    # 职位选择
    st.markdown("<h4 style='margin-bottom: 16px;'>💼 目标职位</h4>", unsafe_allow_html=True)
    
    job_type = st.selectbox(
        "选择职位",
        ["Python开发工程师", "Java开发工程师", "算法工程师", "前端开发工程师", "全栈开发工程师", "数据分析师"],
        key="job_select",
        label_visibility="collapsed"
    )
    
    if st.button("🚀 开始面试", type="primary", use_container_width=True):
        if st.session_state["resume_info"]:
            job_desc = {"job_type": job_type}
            st.session_state["job_desc"] = job_desc
            
            with st.spinner("🎯 生成个性化面试题..."):
                questions = st.session_state["interview_service"].start_interview(
                    st.session_state["resume_info"], 
                    job_desc
                )
                st.session_state["questions"] = questions
                st.session_state["current_question_index"] = 0
                st.session_state["evaluations"] = []
                st.session_state["messages"] = [
                    {"role": "assistant", "content": f"👋 欢迎参加{job_type}面试！我是你的AI面试官。我会根据你的简历背景进行针对性提问，请放松心情，展示你的真实水平。"}
                ]
                # 关键修复：重置输入相关状态
                st.session_state["answer_input"] = ""
                st.session_state["input_key_counter"] += 1
            
            st.rerun()
        else:
            st.error("❌ 请先解析简历后再开始面试")

# 主内容区域
st.markdown("<h1 style='text-align: center; margin-bottom: 8px; background: linear-gradient(90deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>🤖 AI 智能面试系统</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 32px;'>基于大语言模型的个性化技术面试模拟平台</p>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    # 聊天区域
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 0; display: flex; align-items: center; gap: 8px;'><span style='font-size: 24px;'>💬</span> 面试对话</h3>", unsafe_allow_html=True)
    
    # 聊天容器
    chat_container = st.container(height=450)
    with chat_container:
        for message in st.session_state["messages"]:
            if message["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 回答输入区域 - 关键修复：使用动态key确保清空生效
    if st.session_state["questions"] and st.session_state["current_question_index"] < len(st.session_state["questions"]):
        st.markdown("<div class='glass-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
        
        current_q = st.session_state["questions"][st.session_state["current_question_index"]]
        
        st.markdown(f"""
        <div class='question-card'>
            <div style='color: #58a6ff; font-size: 12px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;'>
                问题 {st.session_state["current_question_index"] + 1} / {len(st.session_state["questions"])} · {current_q.get('type', '技术问题')}
            </div>
            <div style='color: #f0f6fc; font-size: 16px; line-height: 1.6; font-weight: 500;'>
                {current_q.get('question', '无')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 关键修复：使用动态key，每次提交后改变key值强制刷新输入框
        input_key = f"answer_input_{st.session_state['input_key_counter']}"
        
        answer = st.text_area(
            "你的回答",
            value=st.session_state["answer_input"],
            height=150,
            placeholder="请在此输入你的回答...建议结构化表达，突出重点。",
            key=input_key,
            label_visibility="collapsed"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            submit_btn = st.button("📤 提交回答", type="primary", use_container_width=True)
        
        with col_btn2:
            skip_btn = st.button("⏭️ 跳过", use_container_width=True)
        
        with col_btn3:
            hint_btn = st.button("💡 提示", use_container_width=True)
        
        if submit_btn:
            if answer.strip():
                # 添加用户回答到对话
                st.session_state["messages"].append({
                    "role": "user", 
                    "content": f"**我的回答：**\n{answer}"
                })
                
                # 评估回答
                with st.spinner("🧠 AI正在评估..."):
                    evaluation = st.session_state["interview_service"].evaluate_answer(
                        current_q.get('type', '技术问题'),
                        current_q.get('question', ''),
                        answer
                    )
                    st.session_state["evaluations"].append(evaluation)
                
                # 构建反馈
                score_color = "#3fb950" if evaluation['score'] >= 4 else "#d29922" if evaluation['score'] >= 3 else "#f85149"
                
                feedback_msg = f"""
                <div style='background: rgba(22, 27, 34, 0.6); padding: 16px; border-radius: 12px; margin-top: 8px;'>
                    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 12px;'>
                        <span style='font-size: 20px;'>📊</span>
                        <span style='color: #f0f6fc; font-weight: 600;'>回答评分：</span>
                        <span style='background: {score_color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 700;'>
                            {evaluation['score']}/5
                        </span>
                    </div>
                    <div style='color: #8b949e; font-size: 14px; line-height: 1.6;'>
                        <strong style='color: #f0f6fc;'>改进建议：</strong><br>
                """
                for fb in evaluation['feedback']:
                    feedback_msg += f"• {fb}<br>"
                feedback_msg += "</div></div>"
                
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": feedback_msg
                })
                
                # 关键修复：增加计数器改变key，强制刷新输入框
                st.session_state["current_question_index"] += 1
                st.session_state["answer_input"] = ""
                st.session_state["input_key_counter"] += 1
                
                st.rerun()
            else:
                st.warning("⚠️ 请输入回答内容")
        
        if skip_btn:
            st.session_state["current_question_index"] += 1
            st.session_state["answer_input"] = ""
            st.session_state["input_key_counter"] += 1
            st.rerun()
        
        if hint_btn:
            hint_msg = f"💡 **提示：** {current_q.get('hint', '建议从实际项目经验出发，结合具体技术细节回答。')}"
            st.session_state["messages"].append({
                "role": "assistant",
                "content": hint_msg
            })
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 面试完成
    elif st.session_state["questions"] and st.session_state["current_question_index"] >= len(st.session_state["questions"]):
        st.markdown("<div class='glass-card' style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
        
        if st.session_state["evaluations"]:
            avg_score = sum(e['score'] for e in st.session_state["evaluations"]) / len(st.session_state["evaluations"])
            
            st.markdown(f"""
            <div style='margin-bottom: 24px;'>
                <div style='font-size: 48px; margin-bottom: 16px;'>🎉</div>
                <h2 style='color: #f0f6fc; margin-bottom: 8px;'>面试完成！</h2>
                <p style='color: #8b949e;'>感谢你的参与，以下是本次面试总结</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_score1, col_score2, col_score3 = st.columns(3)
            with col_score1:
                st.metric("平均得分", f"{avg_score:.1f}/5")
            with col_score2:
                st.metric("总问题数", len(st.session_state["questions"]))
            with col_score3:
                best_score = max(e['score'] for e in st.session_state["evaluations"])
                st.metric("最高单题得分", f"{best_score}/5")
            
            # 综合评价
            if avg_score >= 4:
                evaluation_text = "🌟 **优秀表现！** 你的技术基础扎实，表达清晰，建议继续保持！"
            elif avg_score >= 3:
                evaluation_text = "👍 **良好表现！** 整体不错，但在某些技术细节上可以更深入。"
            else:
                evaluation_text = "💪 **继续加油！** 建议加强基础知识学习，多进行模拟练习。"
            
            st.info(evaluation_text)
            
            if st.button("🔄 重新开始面试", type="primary", use_container_width=True):
                st.session_state["questions"] = []
                st.session_state["current_question_index"] = 0
                st.session_state["evaluations"] = []
                st.session_state["answer_input"] = ""
                st.session_state["input_key_counter"] += 1
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "你好！我是AI面试官。请先上传简历和选择职位，然后我们开始模拟面试。"}
                ]
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    # 进度面板
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top: 0; text-align: center;'>📊 面试进度</h3>", unsafe_allow_html=True)
    
    if st.session_state["questions"]:
        current_idx = st.session_state["current_question_index"]
        total = len(st.session_state["questions"])
        progress = (current_idx / total) if total > 0 else 0
        
        st.progress(progress, text=f"进度 {current_idx}/{total}")
        
        # 统计信息
        if st.session_state["evaluations"]:
            avg_so_far = sum(e['score'] for e in st.session_state["evaluations"]) / len(st.session_state["evaluations"])
            st.markdown(f"""
            <div style='background: #21262d; padding: 16px; border-radius: 10px; margin-top: 16px; text-align: center;'>
                <div style='color: #8b949e; font-size: 12px; margin-bottom: 4px;'>当前平均得分</div>
                <div style='color: #f0f6fc; font-size: 28px; font-weight: 700;'>{avg_so_far:.1f}<span style='font-size: 16px; color: #8b949e;'>/5</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px; color: #8b949e;'>
            <div style='font-size: 32px; margin-bottom: 12px;'>🤔</div>
            <p>尚未开始面试<br>请在左侧准备简历并开始</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 历史评估
    if st.session_state["evaluations"]:
        st.markdown("<div class='glass-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0;'>📈 答题历史</h3>", unsafe_allow_html=True)
        
        for i, ev in enumerate(st.session_state["evaluations"]):
            score_color = "#3fb950" if ev['score'] >= 4 else "#d29922" if ev['score'] >= 3 else "#f85149"
            
            with st.expander(f"问题 {i+1} 详情", expanded=False):
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 12px;'>
                    <span style='color: #f0f6fc; font-weight: 600;'>评分：</span>
                    <span style='background: {score_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 14px; font-weight: 600;'>
                        {ev['score']}/5
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                if 'breakdown' in ev:
                    st.markdown("<div style='color: #8b949e; font-size: 13px; margin-bottom: 8px;'><strong style='color: #f0f6fc;'>维度分析：</strong></div>", unsafe_allow_html=True)
                    for dim, score in ev['breakdown'].items():
                        st.markdown(f"<div style='display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 13px;'><span style='color: #8b949e;'>{dim}</span><span style='color: #f0f6fc;'>{score:.1f}</span></div>", unsafe_allow_html=True)
                
                st.markdown("<div style='color: #8b949e; font-size: 13px; margin-top: 12px;'><strong style='color: #f0f6fc;'>建议：</strong></div>", unsafe_allow_html=True)
                for fb in ev['feedback'][:2]:  # 只显示前两条建议
                    st.markdown(f"<div style='color: #c9d1d9; font-size: 13px; margin-bottom: 4px;'>• {fb}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 面试技巧提示
    st.markdown("<div class='glass-card' style='margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top: 0; color: #58a6ff;'>💡 面试技巧</h4>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #8b949e; font-size: 13px; line-height: 1.8;'>
        • <strong style='color: #c9d1d9;'>STAR法则</strong>：情境-任务-行动-结果<br>
        • <strong style='color: #c9d1d9;'>结构化表达</strong>：总分总结构<br>
        • <strong style='color: #c9d1d9;'>具体案例</strong>：用项目经历支撑观点<br>
        • <strong style='color: #c9d1d9;'>诚实回答</strong>：不懂就说不懂，不要编造
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)