import os
from typing import TypedDict, List
import json

# 1. 强制国内镜像源，防止模型校验失败
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 引入核心组件
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==========================================
# 模块 A：加载本地 RAG 检索引擎
# ==========================================
class LocalHuggingFaceEmbedding(EmbeddingFunction):
    def __init__(self, model_name="BAAI/bge-large-zh-v1.5"):
        # 已经下载过了，这次会直接秒开
        self.model = SentenceTransformer(model_name)
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()

print("🔌 正在连接本地医疗向量数据库...")
chroma_client = chromadb.PersistentClient(path="./medical_db")
medical_collection = chroma_client.get_collection(
    name="medical_docs", 
    embedding_function=LocalHuggingFaceEmbedding()
)

# ==========================================
# 模块 B：初始化通义千问最强推理大脑 (对外导出 llm)
# ==========================================
# ⚠️ 推荐做法：将 API KEY 存放在同目录的 .env 文件中：DASHSCOPE_API_KEY=sk-xxxx
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-这里填入你的真实 API KEY 用于备用")

# 实例化大模型 (导出给 memory_manager 使用)
llm = ChatOpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max", # 使用最强推理模型
    temperature=0.3
)

# ==========================================
# 模块 C：LangGraph 多智能体工作流 (DAG 大脑)
# ==========================================

# 1. 定义全局白板 (State：多智能体共享的数据状态)
class AgentState(TypedDict):
    user_query: str          # 患者最新的提问
    chat_history: list       # 患者与AI医生的多轮对话历史字典列表 (JSON列表格式)
    user_profile: dict       # 👈 [关键技术点] 用户的长期病历画像 (JSON字典格式)
    risk_level: str          # 风险等级 (RED/GREEN)
    retrieved_docs: str      # 查到的本地权威知识
    final_response: str      # AI 最终生成的建议

# 2. 定义节点 (Nodes)
def triage_node(state: AgentState):
    """【节点1：分诊台 Agent】负责判断是否触发致命熔断"""
    print("\n🩺 [智能分诊台] 正在进行风险把关...")
    query = state["user_query"]
    
    # 算法级风控黑名单
    if "胸闷" in query and "骤降" in query:
        state["risk_level"] = "RED"
        state["final_response"] = "🚨 【系统最高级别预警】检测到心源性高危症状（HRV骤降并发胸闷），请立刻停止一切剧烈活动，立即拨打 120 急救电话！您的健康重于一切，我们强制中断了 AI 对话流程，请务必先解决致命风险！"
    else:
        state["risk_level"] = "GREEN"
    return state

def rag_node(state: AgentState):
    """【节点2：文献检索 Agent】纯本地断网检索权威指南"""
    print("📚 [本地检索引擎] 正在档案室查阅权威依据...")
    query = state["user_query"]
    
    # 调动本地 BGE 模型算距离，进行语义搜索
    results = medical_collection.query(query_texts=[query], n_results=2)
    docs = "\n".join(results['documents'][0])
    
    state["retrieved_docs"] = docs
    print(f"   -> 命中知识片段摘要：{docs[:30]}...") 
    return state

# 👇 这是你刚才没找到的代码，现在加上了长期记忆和短期滑动
def doctor_node(state: AgentState):
    """【节点3：主治医师 Agent】融合记忆、知识库与推理，输出方案"""
    print("👨‍⚕️ [主治医师 Agent] 正在结合全链路记忆与知识库协同研判...")
    
    # 提取多方数据
    query = state["user_query"]
    docs = state["retrieved_docs"]
    profile_dict = state.get("user_profile", {}) # 长期病历画像
    history_list = state.get("chat_history", [])  # 近期对话

    # 1. 👈 [优化核心逻辑]：在大脑内实现滑动窗口，提取最近 6 条（3轮）短期追问记忆
    sliding_window_msgs = history_list[-6:]
    history_str = "无"
    if sliding_window_msgs:
        history_str = "\n".join([
            f"{'患者' if msg['role']=='user' else 'AI医生'}: {msg['content']}" 
            for msg in sliding_window_msgs
        ])
    
    # 2. 👈 [关键技术点] 格式化长期画像 JSON
    profile_str = json.dumps(profile_dict, ensure_ascii=False, indent=2)
    
    # 3. 组装企业级严谨的超级 Prompt 
    prompt = f"""
    你是一位专业的“中西医结合私人健康顾问”。请结合以下【全链路记忆信息】，解答患者最新的提问。
    注意：在回答既往病史和过敏史相关的问题时，必须以【长期健康画像（核心记忆）】为准，不可给出冲突甚至危险的建议！需融合中西医干预方案。

    ========================
    📖 [患者长期健康画像（核心记忆）]：
    {profile_str}
    
    📖 [本地医学指南]：
    {docs}
    
    📖 [最近多轮对话上下文（短期记忆）]：
    {history_str}
    
    ========================
    
    【患者最新提问】：
    {query}
    """
    
    # 构建发给 API 的消息列表
    messages = [
        SystemMessage(content="你是一个严谨的医疗Agent，不产生幻觉，尊重患者隐私，能联系短期记忆和长期病历精准回答。"),
        HumanMessage(content=prompt)
    ]
    
    # 发送给通义千问 API 
    response = llm.invoke(messages)
    
    state["final_response"] = response.content
    return state

# 3. 画图编排流水线 (Edges与有向图生成)
workflow = StateGraph(AgentState)

# 把人安排进图里
workflow.add_node("Triage", triage_node)
workflow.add_node("RAG", rag_node)
workflow.add_node("Doctor", doctor_node)

# 从分诊台开始
workflow.set_entry_point("Triage")

# 设道路标：红灯直接结束，绿灯去查资料
workflow.add_conditional_edges(
    "Triage",
    lambda state: "End" if state["risk_level"] == "RED" else "Continue",
    {
        "End": END,
        "Continue": "RAG"
    }
)

# 正常流程：查完资料 -> 交给大夫 -> 结束
workflow.add_edge("RAG", "Doctor")
workflow.add_edge("Doctor", END)

# 编译成最终的 Agent 引擎 (对外导出给 app.py 使用)
YueYang_Agent = workflow.compile()