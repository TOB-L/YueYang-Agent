# 🏥 YueYang - Medical-Grade Multi-Agent Health Advisory System

[English](./README.en.md) | [中文简体](./README.md)

> 🏆 **2025 Alibaba Large Model Application Top Competition · National Finalist**
> 👑 **Hangzhou AI Workshop Exclusive Invited Personal Project**
> 
> **YueYang** is a highly autonomous personal health advisory Agent. It integrates Chinese and Western medicine dual-mode reasoning logic, featuring full-modality data perception, long/short-term dual-state memory networks, and a zero-hallucination RAG retrieval engine, aiming to provide safe, precise, and personalized health intervention plans.

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![LLM Engine](https://img.shields.io/badge/LLM-Qwen_Max_|_VL_|_Audio-purple.svg)](https://help.aliyun.com/zh/dashscope/)
[![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-green.svg)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🧠 System Architecture

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
        VDB -.->|Embeddings| MedDocs[Medical Guidelines / Classic TCM Texts]
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
```

---

## 📈 Project Evolution

This project has completed a deep refactoring from "business logic validation" to "fully autonomous underlying infrastructure":

* **Phase 1: Business Loop & Model Validation (V1.0)**
    * Rapidly verified the feasibility of "integrated Chinese and Western medicine intervention" and "multi-modal health records" based on the Alibaba Bailian platform, successfully earning a spot in the national finals.
* **Phase 2: Native Core Refactoring (V2.0 Native Core) 👈 `Current Status`**
    * To break through black-box limitations and performance bottlenecks, **the Agentic Workflow was rebuilt entirely using native Python**.
    * Autonomously implemented underlying Function Calling protocols, a local medical RAG system based on ChromaDB, and multi-tenant isolated memory streams.

---

## 🚀 Technical Highlights

### 1. End-to-End Multi-modality Perception
* **Unstructured Medical Report Parsing:** Natively integrates `Qwen-VL` to achieve precise JSON formatting and extraction from complex medical checkup reports (PDF/Images), discarding fragile OCR pipelines.
* **Audio Direct-to-Memory Architecture:** Bypasses traditional ASR, routing audio pulses directly to the multi-modal LLM to significantly reduce interaction latency.

### 2. Zero-Hallucination Medical RAG
* **Authoritative Local Knowledge Base:** Powered by ChromaDB, slicing and indexing highly authoritative medical literature specifically for high-risk medical Q&A scenarios.
* **Mandatory Traceability Routing:** Forces the LLM to perform vector retrieval before outputting medical diagnostic bases, ensuring 100% traceability of intervention plans.

### 3. Dual-State Memory Network
* **Short-term Session Isolation:** Achieves precise session state isolation and context time-travel in multi-tenant concurrent environments.
* **Long-term Silent Extraction:** Deploys a "Silent Observer" daemon to automatically detect and extract high-value entity tags (allergies, sleep patterns, chronic diseases) across multiple unstructured conversational turns, persistently building dynamic, personalized health profiles.

### 4. Standardized IoT Integration
* Defines data contracts based on strict JSON Schemas, simulating the integration of external smart wearable device APIs (e.g., Huawei Health, Apple Health), granting the LLM the ability to perceive real-world vital signs.

---

## 📸 Showcase

| **Deep Report Parsing** | **Wearable Data Structuring** |
| :---: | :---: |
| <img width="400" alt="Report Parsing" src="https://github.com/user-attachments/assets/cb890e7c-171a-49d5-9d0c-802359663fe7" /> | <img width="400" alt="IoT Integration" src="https://github.com/user-attachments/assets/b09caec7-346a-4291-9c10-b53963aad797" /> |
| *Extracting key abnormal indicators automatically using vision models* | *Agent autonomously aligns hardware vital sign data* |

<br>

<details>
  <summary><b>👉 Click to expand: 6D Intervention Plan (Complete Case)</b></summary>
  <br>
  <div align="center">
    <img width="800" alt="Comprehensive Plan" src="https://github.com/user-attachments/assets/d08e1709-b00c-434d-8f92-87fab52c4af9" />
    <p><em>Outputting comprehensive plans combining Western red-line warnings and TCM constitution adjustments based on local RAG</em></p>
  </div>
</details>

---

## 🛠️ Quick Start

### Prerequisites
* Python >= 3.10
* Valid Qwen API Key (with access to text, VL, and Audio models)

### Installation
```bash
# 1. Clone the repository
git clone [https://github.com/TOB-L/YueYang-Agent.git](https://github.com/TOB-L/YueYang-Agent.git)
cd YueYang-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment configuration (create a .env file in the root directory)
echo 'QWEN_API_KEY="sk-your-api-key-here"' > .env

# 4. Initialize the local medical knowledge base (ChromaDB)
python yueyang/rag/build_knowledge.py

# 5. Start the service
# Start backend API (if applicable)
python server.py
# Start frontend UI
streamlit run app.py
```

---

## ⚠️ Safety & Compliance

This project strictly adheres to medical and personal data protection regulations at the algorithmic level.

> **Disclaimer:** All intervention plans and data analysis output by the system are for personal health management reference only and **can never replace a face-to-face diagnosis by a licensed professional physician**.

**🚨 Algorithmic Kill-Switch:**
The system features a built-in high-risk symptom detector. When extreme abnormal combinations are detected (e.g., `HRV sudden drop` + `chest tightness`), the Agent forcibly suspends the standard session, directly triggers a `[🚨 RED ALERT]` interruption, and prominently prompts the user to call emergency services (120/911) immediately.

---

<div align="center">
  <i>Built with ❤️ by Renxin Zhihu Team & Zhang Shuai</i>
</div>