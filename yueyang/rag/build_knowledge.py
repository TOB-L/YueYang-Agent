import os
import chromadb
import dashscope
from chromadb import Documents, EmbeddingFunction, Embeddings

# 1. 打造专属的“通义千问翻译官”（将中文文字变成高维向量）
class DashScopeEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
        embeddings = []
        for text in input:
            # 调用通义最新 V2 版本的向量抽取大模型
            resp = dashscope.TextEmbedding.call(
                model=dashscope.TextEmbedding.Models.text_embedding_v2,
                input=text
            )
            if resp.status_code == 200:
                embeddings.append(resp.output["embeddings"][0]["embedding"])
            else:
                embeddings.append([0.0] * 1536) # 防崩溃保底
        return embeddings

# 2. 连接你的本地数据库文件夹
client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_or_create_collection(
    name="medical_docs",
    embedding_function=DashScopeEmbeddingFunction()
)

# 3. 编造几条【只有这个系统才知道】的绝密医学规则（用于测试）
knowledge_texts = [
    "【悦养专属-脂肪肝红线指南】轻度脂肪肝患者如果提问能否吃炸鸡，系统必须立刻发出红色(red)高风险警报！并严厉告知：悦养系统医疗库明确规定，脂肪肝吃炸鸡极易引发急性坏死性胰腺炎，属于绝对禁忌！",
    "【悦养专属-过敏急救守则】如果用户提到自己对海鲜过敏并感到呼吸困难，必须下达紧急行动(urgent: true)，要求立刻使用肾上腺素笔（EpiPen）并拨打120。",
    "【悦养专属-熬夜评估标准】连续熬夜超过3天者，系统应判定为黄色(yellow)中风险，并强制建议补充维生素B族和进行心电图监测。"
]

# 给每条知识贴上标签 ID
ids = [f"doc_{i}" for i in range(len(knowledge_texts))]

# 4. 执行灌注！
print("🧠 正在将医学知识转化为高维向量，并存入本地数据库...")
collection.add(documents=knowledge_texts, ids=ids)
print("✅ 知识库构建完成！你现在的 medical_db 文件夹里已经有数据了！")