# 🏥 悦养 (YueYang) - 智能健康风险预警与多智能体系统

[项目封面]
<img width="1913" height="878" alt="image" src="https://github.com/user-attachments/assets/0fd29771-23da-4643-8b54-f022ee8ed6ea" />

> 🏆 **2026 阿里巴巴大模型应用顶尖赛事 全国决赛入围项目**
> 👑 **杭州 AI 工坊唯一受邀路演学生项目**
> 
> 这是一个融合中西医双模推理，具备全模态感知、长短期双螺旋记忆与零幻觉 RAG 架构的私人健康顾问 Agent。

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/Model-Qwen_Max_|_VL_|_Audio-purple.svg)](https://help.aliyun.com/zh/dashscope/)
[![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-green.svg)](https://www.trychroma.com/)

---

## 📈 项目演进路线 (Project Evolution)

本项目经历了从“商业逻辑验证”到“底层架构完全自主可控”的两次重大迭代，展现了完整的工业级产品研发周期：

- **Phase 1: 业务闭环与参赛验证 (V1.0 MVP)**
  - 依托阿里百炼第三方智能体平台，快速验证“中西医融合干预”与“多模态健康档案”的商业逻辑。
  - 凭借极高的场景契合度与完整的产品设计，**成功斩获AI模型智能体创新大赛顶尖赛事全国决赛资格**。
- **Phase 2: 底层基座自主重构 (V2.0 Native Core) 👈 `当前代码库状态`**
  - 为突破第三方平台的黑盒限制与性能瓶颈，**弃用高度封装的框架，采用纯原生 Python 完全重写了底层架构。**
  - 独立实现了底层的 Agentic Workflow、Function Calling 通信协议、基于 ChromaDB 的本地医学 RAG 系统，以及多租户的长短期记忆隔离。

---

## 🚀 核心架构与技术亮点

### 1. 全模态原生感知 (End-to-End Multi-modality)
- **视觉报告解析:** 摒弃脆弱的 OCR。原生集成 `Qwen-VL` 实现复杂体检报告（PDF/图片）非结构化数据的 JSON 格式化提取。
- **音频内存直驱:** 首创“音频 Base64 内存直驱”策略。语音脉冲直接送入多模态音频大模型，绕过传统 ASR 转换，极大降低交互延迟。

### 2. 零幻觉 RAG 检索引擎 (Zero-Hallucination RAG)
- 针对医疗高危场景，采用 **ChromaDB** 构建本地权威知识库，将《中国高血压防治指南》及《黄帝内经》切片入库。
- 重写 Tool Calling 逻辑，强制大模型在回答医疗严肃问题前执行“向量开卷检索”，实现诊断依据的 100% 溯源。

### 3. 长短期双螺旋记忆 (Dual-Memory System)
- **短期会话隔离:** 实现多租户会话状态的精准切片与时空穿梭。
- **长期画像静默提取:** 独创“静默观察者”组件。在多轮对话中自动侦测并提取用户的“过敏史、作息规律、慢性病史”等长期 Tag 并持久化，实现千人千面的健康画像。

### 4. 插件式数据通信 (Function Calling)
- 定义标准化 JSON Schema，模拟挂载外部智能穿戴设备（华为/Apple Watch）API，赋予大模型感知现实物理世界体征的能力。

---

## 📸 核心功能展示

*(此处保留你原本的动图和截图)*

### 体检报告深度解析
<img width="692" height="500" alt="image" src="https://github.com/user-attachments/assets/cb890e7c-171a-49d5-9d0c-802359663fe7" />
*上传 PDF/图片，系统调用 Qwen-VL 自动提取关键异常指标*

### 可穿戴设备数据结构化
<img width="692" height="311" alt="image" src="https://github.com/user-attachments/assets/b09caec7-346a-4291-9c10-b53963aad797" />
*大模型通过 Tool Calling 自主提取并标准化用户输入的硬件数据*

### 融合中西医的六维干预方案
<img width="972" height="756" alt="image" src="https://github.com/user-attachments/assets/d08e1709-b00c-434d-8f92-87fab52c4af9" />
*基于 RAG 知识库，输出西医红线预警与中医体质调理的综合方案*

---

## ⚠️ 医疗合规与熔断机制 (Safety & Compliance)
本项目严格遵循《互联网诊疗监管细则》与《个人信息保护法》。所有建议仅供健康管理参考，**绝不替代执业医师诊断**。系统内置算法级熔断底线：当侦测到极端高风险症状（如 HRV骤降 + 胸闷）时，强制切断普通对话，触发 `[🚨 红色高风险]` 警报并提示立即拨打 120。

---
*Built with ❤️ by 仁心智护队 & 张帅*
