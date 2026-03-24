from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import List, Dict

# 引入你之前写好的核心大脑和记忆工具 (完全不用改之前的代码！)
from main_agent import YueYang_Agent
from memory_manager import get_user_profile, load_session, save_session, run_memory_summarizer_agent

app = FastAPI(title="悦养 V2.0 核心引擎 API", description="基于 LangGraph 的医疗多智能体后端服务")

# 定义前端传过来的数据格式
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    user_input: str

# 1. 对话核心接口
@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        # 1. 提取参数
        uid = request.user_id
        sid = request.session_id
        query = request.user_input
        
        # 2. 读取硬盘记忆
        history = load_session(uid, sid)
        profile = get_user_profile(uid)
        
        # 3. 把新问题加进历史
        history.append({"role": "user", "content": query})
        
        # 4. 🚀 触发大模型和 LangGraph
        result = YueYang_Agent.invoke({
            "user_query": query,
            "chat_history": history,
            "user_profile": profile
        })
        
        # 5. 提取结果
        level = result.get("risk_level", "GREEN")
        reply = result.get("final_response", "系统异常")
        
        # 6. 保存回答并落盘
        history.append({"role": "assistant", "content": reply})
        save_session(uid, sid, history)
        
        # 7. 返回标准 JSON 给前端
        return {
            "code": 200,
            "risk_level": level,
            "reply": reply
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. 记忆整理接口 (供前端在结束对话时调用)
@app.post("/api/summarize")
async def summarize_memory(user_id: str, session_id: str):
    history = load_session(user_id, session_id)
    # 异步触发隐式提炼
    run_memory_summarizer_agent(user_id, history)
    return {"code": 200, "msg": "后台记忆整理已启动"}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)