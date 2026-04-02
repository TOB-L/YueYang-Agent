# 🏥 YueYang (悦养) - Medical-Grade Multi-Agent Health Advisory System

> 🏆 **2025 阿里巴巴大模型应用顶尖赛事 · 全国决赛入围项目**
> 👑 **杭州 AI 工坊唯一受邀路演个人项目**
> 
> **YueYang (悦养)** 是一个具有高度自主性的私人健康顾问 Agent。它融合了中西医双模推理逻辑，具备全模态数据感知、长短期双态记忆网络以及零幻觉 RAG 检索引擎，旨在提供安全、精准、个性化的健康干预方案。

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/LLM-Qwen_Max_|_VL_|_Audio-purple.svg)](https://help.aliyun.com/zh/dashscope/)
[![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-green.svg)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🧠 系统核心架构 (System Architecture)

```mermaid
graph TD
    User((User)) -->|Text / Audio / Image| UI[Streamlit Frontend]
    UI <--> API[Backend API Server]
    
    subgraph Agentic_Workflow [Agentic Core Workflow]
        API <--> Core[Main Agent Controller]
        Core <-->|Prompt & Reasoning| LLM{Qwen Max / VL / Audio}
        
        Core <-->|Short-term Context| MemS[Session Memory Manager]
        Core <-->|Silent Tagging| MemL[Long-term Portrait Extractor]
        
        Core -->|Tool Calling| RAG[Zero-Hallucination RAG]
        Core -->|Tool Calling| Func[Function & Plugin Calling]
    end
    
    subgraph Local_Knowledge_Base
        RAG <--> VDB[(ChromaDB)]
        VDB -.->|Embeddings| MedDocs[高血压指南 / 黄帝内经等]
    end
    
    subgraph External_Environment
        Func <--> IoT[Wearable IoT APIs]
        Func <--> Vision[Medical Report Parser]
    end
    
    classDef primary fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef secondary fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef db fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    
    class Core,LLM primary;
    class MemS,MemL,RAG,Func secondary;
    class VDB db;