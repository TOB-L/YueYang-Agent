import streamlit as st
import os
import json
import datetime

# 引入核心大脑和视觉解析工具
from call_qwen import call_qwen_once
try:
    from call_qwen_vl import parse_medical_image
except ImportError:
    pass 

st.set_page_config(page_title="悦养 - 风险评估舱", page_icon="🏥", layout="wide")

# ================= 0. 核心本地存储引擎 (新增) =================
def get_history_dir(user_id):
    """获取用户的专属历史文件夹"""
    dir_path = f"history_db_{user_id}"
    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def load_session(user_id, session_name):
    """读取某一次历史会话"""
    file_path = os.path.join(get_history_dir(user_id), session_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_session(user_id, session_name, history_data):
    """保存当前会话到硬盘"""
    file_path = os.path.join(get_history_dir(user_id), session_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

# ================= 1. 账号体系拦截网 =================
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>👋 欢迎登录 悦养系统</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>私人专属的 AI 健康管家</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container(border=True):
            st.subheader("📱 手机号快捷登录")
            phone_number = st.text_input("请输入手机号码", placeholder="例如：13800138000")
            #纯UI占位
            sms_code = st.text_input("验证码 (Demo阶段随便填)", type="password")
            if st.button("🚀 登录 / 注册", use_container_width=True):
                if len(phone_number) >= 11:
                    st.session_state.user_id = phone_number
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("请输入有效的手机号码！")
    st.stop()

# 初始化当前会话的 ID
if "current_session" not in st.session_state:
    st.session_state.current_session = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "assistant",
        "content": "您好！我是您的私人健康助手。请在下方输入症状、发送语音，或点击 ➕ 上传图片/体检文件。"
    }]


# ================= 2. 侧边栏：真实历史会话 (完全重构) =================
with st.sidebar:
    st.success(f"👤 当前在线: {st.session_state.user_id}")
    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.subheader("📚 历史会话")
    
    # 【新建咨询】按钮：生成新文件名，清空屏幕
    if st.button("➕ 新建健康咨询", type="primary", use_container_width=True):
        st.session_state.current_session = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "开启了一段新的健康咨询。请描述您的状况。"
        }]
        st.rerun()
        
    st.markdown("---")
    
    # 动态读取用户的硬盘文件夹，生成历史记录按钮
    history_dir = get_history_dir(st.session_state.user_id)
    saved_files = sorted([f for f in os.listdir(history_dir) if f.endswith(".json")], reverse=True)
    
    if not saved_files:
        st.caption("暂无历史记录")
    else:
        for file_name in saved_files:
            # 把文件名变得好看点，比如 2026-03-13 15:30
            display_name = file_name.replace("session_", "").replace(".json", "")
            try:
                dt = datetime.datetime.strptime(display_name, "%Y%m%d_%H%M%S")
                display_name = dt.strftime("%m-%d %H:%M") + " 的咨询"
            except:
                pass
                
            # 点击历史按钮：读取对应的 JSON 文件覆盖当前屏幕
            if st.button(f"💬 {display_name}", key=file_name, use_container_width=True):
                st.session_state.current_session = file_name
                st.session_state.chat_history = load_session(st.session_state.user_id, file_name)
                st.rerun()

# ================= 3. 主区域：聊天舱 =================
st.title("🏥 悦养 - 智能健康风险预警系统")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ================= 4. 多模态悬浮工具栏 =================
st.markdown("<br>", unsafe_allow_html=True)
col_attach, col_audio, _ = st.columns([1.5, 1.5, 7])

uploaded_file = None
audio_bytes = None

with col_attach:
    with st.popover("➕ 上传附件", use_container_width=True):
        st.markdown("**支持图片与体检单**")
        uploaded_file = st.file_uploader("格式：JPG, PNG, PDF", type=["png", "jpg", "jpeg", "pdf"], label_visibility="collapsed")

with col_audio:
    try:
        from audio_recorder_streamlit import audio_recorder
        audio_bytes = audio_recorder(text="点击录音", icon_name="microphone", icon_size="lg")
    except ImportError:
        st.button("🎤 未安装", disabled=True)

# 全局吸底聊天框
text_input = st.chat_input("请描述您的健康状况或报告疑问...")

# ================= 5. 输入流路由处理 =================
user_input = None

if text_input:
    user_input = text_input

elif audio_bytes:
    # 终极免坑版多模态音频 (Qwen-Audio)
    with st.spinner("🎤 正在让多模态大模型直接听取您的语音..."):
        import base64, dashscope
        from dashscope import MultiModalConversation
        try:
            dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
            if not dashscope.api_key:
                user_input = "（⚠️ 警告：系统未检测到 API Key，请配置后重试）"
            else:
                b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                audio_data_url = f"data:;base64,{b64_audio}"
                
                messages = [{"role": "user", "content": [
                    {"audio": audio_data_url},
                    {"text": "请将这段语音转写为文字。只输出语音里说的内容本身，绝对不要输出多余解释。"}
                ]}]
                
                response = MultiModalConversation.call(model="qwen-audio-turbo", messages=messages)
                
                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    real_text = ""
                    if isinstance(content, list):
                        for item in content:
                            if "text" in item: real_text += item["text"]
                    else:
                        real_text = str(content)
                    st.toast("✅ 大模型听音解码成功！")
                    user_input = real_text 
                else:
                    user_input = f"（大模型听音失败！原因：{response.message}）"
        except Exception as e:
            user_input = f"（系统内部异常，详情：{e}）"

elif uploaded_file is not None:
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        st.session_state.last_uploaded = uploaded_file.name
        with st.spinner("👁️ 正在利用视觉大模型解析文件..."):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            try:
                from call_qwen_vl import parse_medical_image
                vl_result = parse_medical_image(tmp_file_path)
            except Exception as e:
                vl_result = "图片解析模块加载异常。"
            os.remove(tmp_file_path)
            
            # 保存图片的解析记录
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"**已完成结构化解析：** \n\n{vl_result}\n\n*您可以基于此结果继续向我提问。*"
            })
            save_session(st.session_state.user_id, st.session_state.current_session, st.session_state.chat_history)
            st.rerun()

# ================= 6. 触发大模型核心大脑 =================
if user_input:
    # 1. 把用户的输入存进去
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    save_session(st.session_state.user_id, st.session_state.current_session, st.session_state.chat_history)
    
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("🧠 智能体调取记忆与分析中..."):
            result_json, usage = call_qwen_once(
                user_input=user_input,
                chat_history=st.session_state.chat_history,
                user_id=st.session_state.user_id
            )
            
            color_map = {"green": "✅ 低风险 (Green)", "yellow": "⚠️ 中风险 (Yellow)", "red": "🚨 高风险 (Red)"}
            level = result_json.get("risk_level", "green")
            rationale = result_json.get("rationale", "无")
            actions = result_json.get("action_list", [])
            
            ui_color = "#e6f4ea" if level=="green" else "#fef7e0" if level=="yellow" else "#fce8e6"
            
            html_content = f"""
            <div style="background-color: {ui_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h4 style="margin-top:0;">{color_map.get(level, level)}</h4>
                <p><strong>依据：</strong> {rationale}</p>
            </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
            
            reply_text = f"**风险评估：** {color_map.get(level, level)}\n**依据：** {rationale}\n\n"
            for action in actions:
                st.markdown(f"- 步骤 {action['step']}: {action['text']} {'(紧急!)' if action.get('urgent') else ''}")
                reply_text += f"- 步骤 {action['step']}: {action['text']}\n"
                
            # 2. 把 AI 的回复存进去
            st.session_state.chat_history.append({"role": "assistant", "content": reply_text})
            # 3. 再次保存到硬盘
            save_session(st.session_state.user_id, st.session_state.current_session, st.session_state.chat_history)