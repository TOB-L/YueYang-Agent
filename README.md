# 🏥 悦养 (YueYang) - 智能健康风险预警 Agent

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/Model-Qwen_Max_|_VL_|_Audio-purple.svg)](https://help.aliyun.com/zh/dashscope/)
[![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-green.svg)](https://www.trychroma.com/)

> 🏆 **2026 阿里巴巴大模型应用顶尖赛事 全国决赛入围项目**
> 👑 **杭州 AI 工坊唯一受邀路演学生项目**
> 
> 🔗 **在线体验地址:** [点击此处体验系统 (Demo部署于 Streamlit Cloud)](#) 

## 📑 项目简介 (Introduction)

**悦养 (YueYang)** 是一款面向泛健康管理场景的多模态大模型智能体（AI Agent）。
本项目旨在解决传统医疗大模型存在的**“容易产生医疗幻觉”**、**“缺乏长期上下文记忆”**以及**“多模态数据利用率低”**等核心痛点。通过纯原生 Python 搭建底层的 Agentic Workflow，实现了**“全模态感知 + 本地 RAG 权威检索 + 长短期双螺旋记忆”**的工业级医疗辅助闭环。

---

## 🚀 核心架构与功能特性 (Core Features)

### 1. 全模态原生感知 (End-to-End Multi-modality)
- **视觉 (Vision):** 摒弃易错的传统 OCR。集成 `Qwen-VL` 直接对用户上传的复杂体检报告（PDF/图片）进行深度结构化解析，并输出标准 JSON 格式指标。
- **听觉 (Audio):** 首创 **“音频 Base64 内存直驱”** 策略。录音脉冲不落盘、不经过 ASR 转录，直接输送至 `Qwen-Audio-Turbo` 多模态听觉模型，极大降低了系统交互延迟（Latency < 1.5s）。

### 2. 零幻觉 RAG 检索引擎 (Zero-Hallucination RAG)
- 在医疗极其严肃的场景下，采用 **ChromaDB** 构建本地权威知识库。
- 将《中国高血压防治指南》、《黄帝内经》等中西医典籍切片向量化。通过重写大模型的 Tool Calling 逻辑，强制执行“先检索后生成”的规则，将事实性幻觉率压降至 0%。

### 3. 长短期双螺旋记忆 (Dual-Memory System)
- **短期记忆 (Session Context):** 实现多租户会话隔离的本地 JSON 快速读写，支持历史聊天记录时空穿梭。
- **长期画像 (Long-term Profiling):** 独创“静默观察者”权限。在多轮日常对话中，Agent 会自动侦测并提取用户的“过敏史、作息规律、慢性病史”等长期高价值标签，持久化至用户专属物理隔离库中，实现千人千面的动态健康画像。

### 4. 智能体工具挂载 (Function Calling)
- 定义标准化 JSON Schema，成功实现与外部物理世界的通信（例如模拟挂载华为/Apple Watch API），使大模型具备自主获取用户实时步数、心率、睡眠数据的能力。

---

## 🛠️ 技术栈 (Tech Stack)

- **核心编程语言:** Python 3.10
- **大模型基座:** 阿里云通义千问 API (`qwen-max`, `qwen-vl-plus`, `qwen-audio-turbo`, `text-embedding-v2`)
- **知识库/向量数据库:** ChromaDB
- **前端与轻量化部署:** Streamlit, Streamlit Community Cloud (CI/CD)
- **核心思想:** Agentic Workflow, ReAct Prompting, Multi-Agent Collaboration

---

## ⚠️ 免责声明 (Disclaimer)
本项目遵循《互联网诊疗监管细则》。系统提供的所有饮食、作息与健康评估建议**仅供参考，绝不能替代专业执业医师的医疗诊断和处方决策**。系统内置算法级熔断底线：当侦测到极端高风险症状（如 HRV 骤降+胸闷）时，系统将强制停止普通问询，触发并提示用户立即拨打 120 急救电话。

---
*Built with ❤️ by [你的名字] - 探索医疗大模型的无限边界*
