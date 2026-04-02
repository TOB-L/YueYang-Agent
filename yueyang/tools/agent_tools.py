# agent_tools.py
import os
import json
import chromadb
import dashscope
from chromadb import Documents, EmbeddingFunction, Embeddings

# ========================================================
# 1. 模拟智能手表数据抓取工具
# ========================================================
def fetch_smartwatch_data(device_brand: str, data_type: str) -> str:
    """模拟从数据库或第三方 API 获取手表数据"""
    print(f"\n[系统后台执行] 正在调用 {device_brand} API 获取 {data_type} 数据...\n")
    
    mock_database = {
        "heart_rate": 88,
        "sleep_hours": 5.2,
        "steps": 12500,
        "blood_pressure": "140/90"
    }
    
    value = mock_database.get(data_type, "暂无数据")
    
    result = {
        "status": "success",
        "device": device_brand,
        "metric": data_type,
        "value": value
    }
    return json.dumps(result, ensure_ascii=False)

wearable_tool_schema = {
    "type": "function",
    "function": {
        "name": "fetch_smartwatch_data",
        "description": "当用户询问自己的心率、睡眠、步数或血压等健康数据，且没有直接提供具体数值时，调用此工具从智能手表获取实时数据。",
        "parameters": {
            "type": "object",
            "properties": {
                "device_brand": {
                    "type": "string",
                    "description": "设备品牌，例如 'huawei', 'apple', 'xiaomi'。如果用户没说，默认填 'huawei'"
                },
                "data_type": {
                    "type": "string",
                    "enum": ["heart_rate", "sleep_hours", "steps", "blood_pressure"],
                    "description": "需要查询的数据类型：心率(heart_rate)、睡眠(sleep_hours)、步数(steps)、血压(blood_pressure)"
                }
            },
            "required": ["device_brand", "data_type"]
        }
    }
}


# ========================================================
# 2. 真实的 RAG 知识库检索工具 (接入本地 ChromaDB)
# ========================================================
class DashScopeEmbeddingFunction(EmbeddingFunction):
    """专属的向量翻译官，将提问翻译成向量以便在数据库中匹配"""
    def __call__(self, input: Documents) -> Embeddings:
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        embeddings = []
        for text in input:
            resp = dashscope.TextEmbedding.call(
                model=dashscope.TextEmbedding.Models.text_embedding_v2,
                input=text
            )
            if resp.status_code == 200:
                embeddings.append(resp.output["embeddings"][0]["embedding"])
            else:
                embeddings.append([0.0] * 1536) # 防崩溃保底
        return embeddings

def search_medical_knowledge(query: str) -> str:
    """真正的 RAG 向量检索：从本地指南数据库中召回相关条文"""
    print(f"\n[系统后台执行] 正在检索医学知识库，检索词: {query}...\n")
    try:
        # 连接到刚刚建好的本地数据库
        client = chromadb.PersistentClient(path="./medical_db")
        collection = client.get_collection(
            name="medical_docs",
            embedding_function=DashScopeEmbeddingFunction()
        )
        
        # 搜索最相关的 1 条权威指南
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        # 把查到的指南直接返回给大模型
        if results and results['documents'] and results['documents'][0]:
            retrieved_text = results['documents'][0][0]
            return f"【医学知识库权威检索结果】：{retrieved_text}。请严格遵照此结果评估风险并回答用户。"
        else:
            return "知识库中暂未找到相关专属依据，请基于大模型自身医学常识安全作答。"
            
    except Exception as e:
        return f"知识库检索接口异常，报错信息：{e}。请退回使用自身常识作答。"

rag_tool_schema = {
    "type": "function",
    "function": {
        "name": "search_medical_knowledge",
        "description": "当用户询问具体病症、用药指南、饮食禁忌（如高血压、胸闷、失眠、脂肪肝等）时，需要给出专业的医学解释或建议时，**必须**调用此工具检索《医学指南》知识库。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "需要检索的核心医学关键词，例如'脂肪肝 炸鸡'或'海鲜过敏急救'"
                }
            },
            "required": ["query"]
        }
    }
}


# ========================================================
# 3. 长期记忆管理工具（主动侦测批量写入版）
# ========================================================
def update_long_term_memory(memory_dict: dict, user_id: str = "guest") -> str:
    """把用户的长期属性批量写入专属 JSON 文件"""
    print(f"\n[系统后台] 💾 正在更新用户 [{user_id}] 的长期记忆...\n")
    
    file_path = f"memory_{user_id}.json"
    memory = {}
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                memory = json.load(f)
            except:
                pass
                
    if isinstance(memory_dict, dict):
        for key, value in memory_dict.items():
            memory[key] = value
            
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
        
    return f"【长期记忆已更新】：成功记录了 {list(memory_dict.keys())}"

memory_tool_schema = {
    "type": "function",
    "function": {
        "name": "update_long_term_memory",
        "description": "【系统级后台指令】你现在具备'记忆观察者'的权限。在与用户的自然对话中，请默默分析用户的话语。即使用户没有明确要求，只要你侦测到任何具有长期健康管理价值的信息（例如：新的身体症状、生活作息、饮食偏好、确诊疾病、过敏史等），你**必须**主动调用此工具，将这些信息提炼成标签并存入数据库。注意：不要记录无意义的闲聊。",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_dict": {
                    "type": "object",
                    "description": "包含提取出的核心健康档案字典，例如 {'最新症状': '偶尔胸闷', '作息习惯': '凌晨2点睡觉', '忌口': '海鲜'}"
                }
            },
            "required": ["memory_dict"]
        }
    }
}