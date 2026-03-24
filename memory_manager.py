import os
import json
import datetime
from langchain_core.messages import SystemMessage, HumanMessage

# 从大脑中枢导入对外导出的 llm 对象
from main_agent import llm 

# 系统定义画像的标准 JSON 结构
DEFAULT_PROFILE = {
    "基本信息": "未知",
    "确诊既往病史": [],
    "过敏史": "无过敏史记录",
    "生活习惯": [],
    "最近更新时间": "暂未记录"
}

def get_history_dir(user_id):
    """获取用户的专属历史文件夹"""
    dir_path = f"history_db_{user_id}"
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
def load_session(user_id, session_name):
    """读取某一次历史会话的聊天记录"""
    file_path = os.path.join(get_history_dir(user_id), session_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_session(user_id, session_name, history_data):
    """保存当前会话的聊天记录到硬盘"""
    file_path = os.path.join(get_history_dir(user_id), session_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

# ==========================================
# 工具 A：长期病历画像 JSON 的物理读写
# ==========================================

def get_user_profile(user_id):
    """读取用户的长期记忆病历画像 JSON 文件"""
    profile_path = os.path.join(get_history_dir(user_id), "user_profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return DEFAULT_PROFILE.copy() # 如果文件损坏，返回默认
    return DEFAULT_PROFILE.copy() # 如果无文件，返回默认

def save_user_profile(user_id, profile_data):
    """保存用户的长期病历画像 JSON 到硬盘"""
    profile_data["最近更新时间"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    profile_path = os.path.join(get_history_dir(user_id), "user_profile.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)

# ==========================================
# ✨ 核心 B：后台隐式提炼记忆整理 Agent 
# ==========================================

def run_memory_summarizer_agent(user_id, full_chat_history):
    """【后台 Agent】隐式提炼用户的长期病历信息并更新 JSON"""
    print(f"\n🧠 [记忆整理 Agent] 正在后台启动，提炼该用户的咨询摘要...")
    
    # 0. 排除没有真正内容的只有系统开头的那种会话
    if not full_chat_history or len(full_chat_history) < 3: 
        print("   -> 对话太短，无提炼价值。")
        return
# 1. 格式化该次会话的历史对话 (加入强力容错机制)
    history_str_list = []
    for msg in full_chat_history:
        # 确保它是一个正常的字典结构
        if isinstance(msg, dict):
            role = '患者' if msg.get('role') == 'user' else 'AI医生'
            content = msg.get('content', '无内容')
            history_str_list.append(f"{role}: {content}")
        # 如果因为意外混入了纯文本记录，也能安全处理
        elif isinstance(msg, str):
            history_str_list.append(f"系统记录: {msg}")
            
    history_str = "\n".join(history_str_list)
    
    # 2. 组装针对整理画像的超级 Prompt
    summarize_prompt = f"""
    你是一个严谨的医疗记忆整理 Agent。请阅读以下【刚刚结束的咨询对话历史】，从中提取出符合【患者长期病历信息】标准 JSON 结构的有用信息。
    
    【核心原则】：
    1. 只提取已被“确认”的确诊疾病、明确的过敏史、 established 生活习惯（如“吸烟”）。
    2. 不要提取临时的症状（如“头晕几天”）。
    3. 输出必须是 JSON 格式，不含任何解释。
    4. 不要给患者生成最终诊断建议。
    
    【整理好的旧画像（用于增量更新）】：
    {json.dumps(get_user_profile(user_id), ensure_ascii=False, indent=2)}
    
    【剛剛结束的咨询对话历史】：
    {history_str}
    
    请输出严格的 JSON 字符串作为回答：
    """
    
    # 3. 调用 llm 进行提炼 (使用 Qwen-Max 的推理能力)
    messages = [
        SystemMessage(content="你是一个专业的、不产生幻觉的医疗记忆提炼助手。"),
        HumanMessage(content=summarize_prompt)
    ]
    
    try:
        response = llm.invoke(messages)
        
        # 🌟 强力剥壳器：去除大模型经常带有的 ```json 和 ``` 标记
        raw_content = response.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        raw_content = raw_content.strip()
        
        # 安全转换为字典
        response_json = json.loads(raw_content)
        
        # 4. 👈 [关键技术点] 增量更新与智能合并旧画像与新画像
        old_profile = get_user_profile(user_id)
        
        # 智能合并确诊疾病列表 (去重并添加到列表)
        new_病史 = response_json.get("确诊既往病史", [])
        if new_病史:
            merged_disease = list(set(old_profile["确诊既往病史"] + new_病史))
            old_profile["确诊既往病史"] = merged_disease
            
        # 智能合并生活习惯列表 (去重并添加到列表)
        new_习惯 = response_json.get("生活习惯", [])
        if new_习惯:
            merged_habits = list(set(old_profile["生活习惯"] + new_习惯))
            old_profile["生活习惯"] = merged_habits
            
        # 其他字段的覆盖 (如果新画像提供了更精准的信息)
        if "基本信息" in response_json and response_json["基本信息"] != "未知":
            old_profile["基本信息"] = response_json["基本信息"]
            
        if "过敏史" in response_json and response_json["过敏史"] != "无过敏史记录":
            old_profile["过敏史"] = response_json["过敏史"]
            
        if "特殊标记" in response_json:
            old_profile["特殊标记"] = response_json["特殊标记"]

        # 5. 存入硬盘
        save_user_profile(user_id, old_profile)
        print(f"✅ [记忆整理 Agent] 长期病历画像 JSON 已隐式更新完毕。")
        
    except Exception as e:
        print(f"❌ [记忆整理 Agent] 内部整理出错：{e}")