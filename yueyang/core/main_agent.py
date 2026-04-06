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
# [大厂规范改造] 模块：从资产库动态加载 System Prompt
# ==========================================
def load_system_prompt():
    """从本地 .agent_assets 动态加载系统大脑指令"""
    try:
        # 获取当前文件 (main_agent.py) 的上上级目录，即 YueYang-Agent 根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = os.path.join(base_dir, ".agent_assets", "prompts", "system_prompt.txt")
        
        with open(prompt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"⚠️ 警告: 无法读取外部 prompt 资产 ({e})，启用默认安全策略。")
        return "你是一个严谨的医疗Agent，不产生幻觉，尊重患者隐私，能联系短期记忆和长期病历精准回答。"

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
# ⚠️ 注意这里路径：确保你的 medical_db 在运行时能被正确找到
chroma_client = chromadb.PersistentClient(path="./medical_db")
medical_collection = chroma_client.get_collection(
    name="medical_docs", 
    embedding_function=LocalHuggingFaceEmbedding()
)

# ==========================================
# 模块 B：初始化通义千问最强推理大脑
# ==========================================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-这里填入你的真实 API KEY 用于备用")

llm = ChatOpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-max",
    temperature=0.3
)

# ==========================================
# 模块 C：LangGraph 多智能体工作流 (DAG 大脑)
# ==========================================
class AgentState(TypedDict):
    user_query: str          # 患者最新的提问
    chat_history: list       # 近期对话历史
    user_profile: dict       # 长期病历画像
    risk_level: str          # 风险等级
    retrieved_docs: str      # 查到的本地权威知识
    final_response: str      # AI 最终生成的建议

def triage_node(state: AgentState):
    """【节点1：分诊台 Agent】负责判断是否触发致命熔断"""
    print("\n🩺 [智能分诊台] 正在进行风险把关...")
    query = state["user_query"]
    
    if "胸闷" in query and "骤降" in query:
        state["risk_level"] = "RED"
        state["final_response"] = "🚨 【系统最高级别预警】检测到心源性高危症状（HRV骤降并发胸闷），请立刻停止一切剧烈活动，立即拨打 120 急救电话！"
    else:
        state["risk_level"] = "GREEN"
    return state

def rag_node(state: AgentState):
    """【节点2：文献检索 Agent】纯本地断网检索权威指南"""
    print("📚 [本地检索引擎] 正在档案室查阅权威依据...")
    query = state["user_query"]
    
    results = medical_collection.query(query_texts=[query], n_results=2)
    docs = "\n".join(results['documents'][0])
    
    state["retrieved_docs"] = docs
    print(f"   -> 命中知识片段摘要：{docs[:30]}...") 
    return state

def doctor_node(state: AgentState):
    """【节点3：主治医师 Agent】融合记忆、知识库与推理，输出方案"""
    print("👨‍⚕️ [主治医师 Agent] 正在结合全链路记忆与知识库协同研判...")
    
    query = state["user_query"]
    docs = state["retrieved_docs"]
    profile_dict = state.get("user_profile", {})
    history_list = state.get("chat_history", [])

    sliding_window_msgs = history_list[-6:]
    history_str = "无"
    if sliding_window_msgs:
        history_str = "\n".join([
            f"{'患者' if msg['role']=='user' else 'AI医生'}: {msg['content']}" 
            for msg in sliding_window_msgs
        ])
    
    profile_str = json.dumps(profile_dict, ensure_ascii=False, indent=2)
    
    prompt = f"""
    你是一位专业的“中西医结合私人健康顾问”。请结合以下【全链路记忆信息】，解答患者最新的提问。
    注意：必须以【长期健康画像】为准，不可给出冲突建议！需融合中西医干预方案。

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
    
    # [大厂规范改造] 动态读取独立配置的系统指令
    dynamic_sys_prompt = load_system_prompt()
    
    messages = [
        SystemMessage(content=dynamic_sys_prompt),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    state["final_response"] = response.content
    return state

# 画图编排流水线
workflow = StateGraph(AgentState)
workflow.add_node("Triage", triage_node)
workflow.add_node("RAG", rag_node)
workflow.add_node("Doctor", doctor_node)
workflow.set_entry_point("Triage")
workflow.add_conditional_edges(
    "Triage",
    lambda state: "End" if state["risk_level"] == "RED" else "Continue",
    {"End": END, "Continue": "RAG"}
)
workflow.add_edge("RAG", "Doctor")
workflow.add_edge("Doctor", END)

YueYang_Agent = workflow.compile()