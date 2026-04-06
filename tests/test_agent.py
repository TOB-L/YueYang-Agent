import sys
import os

# 将根目录加入路径，以允许导入 yueyang 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yueyang.core.main_agent import triage_node

def test_triage_red_alert():
    """测试：当出现致命症状时，分诊台必须触发 RED 警报"""
    # 模拟患者输入高危词汇
    mock_state = {
        "user_query": "医生，我突然觉得严重胸闷，而且手表提示我心率变异性骤降！",
        "chat_history": [],
        "user_profile": {},
        "risk_level": "",
        "retrieved_docs": "",
        "final_response": ""
    }
    
    # 运行分诊节点
    result_state = triage_node(mock_state)
    
    # 断言：风险等级必须为 RED
    assert result_state["risk_level"] == "RED", "高危症状未触发红色警报！"
    # 断言：必须包含急救提示词
    assert "120" in result_state["final_response"], "警报回复中缺少拨打 120 的提示！"

def test_triage_green_safe():
    """测试：普通咨询时，应为 GREEN 安全状态"""
    mock_state = {
        "user_query": "我最近有点睡不好，想调理一下。",
        "chat_history": [],
        "user_profile": {},
        "risk_level": "",
        "retrieved_docs": "",
        "final_response": ""
    }
    
    result_state = triage_node(mock_state)
    
    # 断言：风险等级必须为 GREEN
    assert result_state["risk_level"] == "GREEN", "普通症状被错误拦截！"