# call_qwen.py
import datetime
import os
import json
import logging
from dashscope import Generation

# 导入你的三个工具：手表、RAG、以及新加的记忆工具
from agent_tools import (
    fetch_smartwatch_data, wearable_tool_schema,
    search_medical_knowledge, rag_tool_schema,
    update_long_term_memory, memory_tool_schema
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("call_qwen_agent")

API_KEY_ENV = "DASHSCOPE_API_KEY"

# 【修改点 1 & 2】：函数接收 user_id，并动态读取专属文件
def build_system_prompt(user_id: str) -> str:
    # 获取真实世界的时间，精确到分钟和星期
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y年%m月%d日 %H:%M (%A)")

    # 动态拼接文件名：比如 memory_13800000000.json
    memory_file = f"memory_{user_id}.json"
    memory_str = "暂无。"
    
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as f:
            try:
                memory_dict = json.load(f)
                memory_str = json.dumps(memory_dict, ensure_ascii=False)
            except:
                pass

    # 组装最强 System Prompt
    return f"""
你是一个专业的私人健康管理大模型 Agent。
【当前登录用户ID】：{user_id}
【当前真实世界时间】：{current_time_str}
【当前用户的长期健康档案】：{memory_str}

你的任务准则：
1. 始终结合当前时间和用户档案来回答问题，展现出你对用户历史的了解。
2. 保持对用户随口提到信息的敏锐度，随时调用记忆工具默默更新档案。
3. 如果用户输入的信息不完整、毫无意义、或者只是普通的问候（比如“你好”），你仍然**必须**进行评估。你可以将风险设为 green，并在 rationale 中用一句话说明“信息不足，请详细描述”。
4. 【最高指令】：你最终返回给用户的回复，必须且只能是一个纯净的 JSON 对象。绝对禁止输出任何 JSON 之外的问候语、解释性纯文本或 markdown 代码块标记！
JSON schema 格式严格如下:
{{"risk_level":"green|yellow|red","action_list":[{{"step":1,"text":"建议文本","urgent":false}}],"rationale":"简短解释"}}
"""
#【修改点 3】：主函数接收 user_id (默认为 "guest")
def call_qwen_once(user_input: str, chat_history: list = None, user_id: str = "guest"):
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"环境变量 {API_KEY_ENV} 未设置")

    # 把 user_id 传给 Prompt 构建函数
    messages = [{"role": "system", "content": build_system_prompt(user_id)}]
    
    # 截取最近的历史记录
    if chat_history:
        recent_history = chat_history[-10:] 
        for msg in recent_history:
            role = "user" if msg["role"] == "user" else "assistant"
            content_str = msg["content"]
            messages.append({"role": role, "content": content_str})
            
    messages.append({"role": "user", "content": user_input})
    tools = [wearable_tool_schema, rag_tool_schema, memory_tool_schema]

    # ============== 第一轮调用 ==============
    response = Generation.call(
        model="qwen-max",
        messages=messages,
        tools=tools,
        result_format='message',
        api_key=api_key
    )

    first_message = response.output.choices[0].message
    messages.append(first_message)
    
    tool_calls = first_message.get("tool_calls") if isinstance(first_message, dict) else getattr(first_message, "tool_calls", None)
    if tool_calls:
        tool_call = tool_calls[0]
        
        # try-except 保护伞
        try:
            if isinstance(tool_call, dict):
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
            else:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
        except Exception as e:
            func_name = "解析错误"
            func_args = {}
            logger.warning("⚠️ 大模型输出了畸形的工具参数，已被系统拦截。")
            
        logger.info(f"💡 大模型请求调用工具: {func_name}, 参数: {func_args}")
        
        # 👇👇👇 注意这里！这些 if 和 elif 必须向右缩进，和上面的 logger.info 对齐！ 👇👇👇
        if func_name == "fetch_smartwatch_data":
            tool_result = fetch_smartwatch_data(
                device_brand=func_args.get("device_brand", "huawei"),
                data_type=func_args.get("data_type")
            )
        elif func_name == "search_medical_knowledge":
            tool_result = search_medical_knowledge(query=func_args.get("query"))
        elif func_name == "update_long_term_memory":
            tool_result = update_long_term_memory(
                memory_dict=func_args.get("memory_dict", {}),
                user_id=user_id 
            )
        else:
            tool_result = f"未知工具: {func_name}"

        messages.append({"role": "tool", "content": tool_result, "name": func_name})
        # ============== 第二轮调用 ==============
        final_response = Generation.call(
            model="qwen-max",
            messages=messages,
            tools=tools,
            result_format='message',
            api_key=api_key
        )
        final_msg = final_response.output.choices[0].message
        final_text = final_msg.get("content", "") if isinstance(final_msg, dict) else final_msg.content
    else:
        final_text = first_message.get("content", "") if isinstance(first_message, dict) else first_message.content

    # ============== 提取最终 JSON ==============
    try:
        if not final_text: raise ValueError("模型返回的内容为空")
        first = final_text.find("{")
        last = final_text.rfind("}")
        if first == -1 or last == -1: raise ValueError(f"未在回答中找到 JSON 结构")
        json_text = final_text[first:last+1]
        parsed = json.loads(json_text)
    except Exception as e:
        logger.error(f"解析 JSON 失败: {str(e)}")
        parsed = {"risk_level": "yellow", "rationale": f"系统解析异常: {str(e)}", "action_list": []}

    return parsed, {"total_tokens": "动态计算"}