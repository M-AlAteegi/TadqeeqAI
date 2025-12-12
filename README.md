# TadqeeqAI 🏛️

### AI-Powered Bilingual Islamic Finance Regulatory Compliance Assistant

A Retrieval-Augmented Generation (RAG) system that provides accurate, citation-backed answers to regulatory compliance questions for Saudi Arabian Islamic finance laws in **both English and Arabic**.

<p align="center">
  <img src="images/welcome_screen.png" alt="TadqeeqAI Welcome Screen" width="800"/>
</p>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🌍 **Bilingual** | Query in English or Arabic - responses in the same language |
| 🔍 **Hybrid Search** | BM25 + Semantic search with Reciprocal Rank Fusion |
| 📊 **Dual Regulators** | SAMA + CMA documents (1,350+ articles) |
| 💬 **Chat History** | Persistent conversations with delete functionality |
| 🎯 **Smart Detection** | Auto-routes queries to relevant regulator |
| 🤖 **Follow-up Support** | Ask for simplification or examples |
| 🔒 **Fully Local** | All data stays on your machine |

---

## 🖼️ Screenshots

### English Query Response
<p align="center">
  <img src="images/query_response.png" alt="English Query Response" width="800"/>
</p>

### Arabic Query Response (RTL Support)
<p align="center">
  <img src="images/query_response_ar.png" alt="Arabic Query Response" width="800"/>
</p>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [Ollama](https://ollama.com/) installed (auto-starts with the app)
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/M-AlAteegi/TadqeeqAI.git
cd TadqeeqAI

# Install dependencies
pip install -r requirements.txt

# Download the LLM
ollama pull aya:8b

# Run the application
python main.py
```

---

## 🗂️ Document Coverage

### SAMA Documents (4 Laws)
| Document | Articles EN | Articles AR |
|----------|-------------|-------------|
| Finance Companies Control Law | ✅ | ✅ |
| Implementing Regulation of Finance Companies | ✅ | ✅ |
| Real Estate Finance Law | ✅ | ✅ |
| Implementing Regulation of Real Estate Finance | ✅ | ✅ |

### CMA Documents (7 Regulations)
| Document | Articles EN | Articles AR |
|----------|-------------|-------------|
| Capital Market Law | ✅ | ✅ |
| Capital Market Institutions Regulations | ✅ | ✅ |
| Investment Funds Regulations | ✅ | ✅ |
| Merger and Acquisition Regulations | ✅ | ✅ |
| Rules on Offer of Securities | ✅ | ✅ |
| Glossary of Defined Terms | ✅ | ✅ |
| Law of Systemically Important Financial Institutions | ✅ | ✅ |

**Total: 1,350+ indexed articles across 22 documents**

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Embeddings** | intfloat/multilingual-e5-base |
| **Vector Database** | ChromaDB |
| **Keyword Search** | BM25 (rank_bm25) |
| **LLM** | Aya 8B via Ollama |
| **Desktop UI** | PyWebView |

---

## 💡 Example Queries

### English
- "What are the licensing fees for finance companies?"
- "What is a qualified investor?"
- "What are the requirements for sukuk issuance?"

### Arabic
- "ما هي رسوم ترخيص شركات التمويل؟"
- "ما هو المستثمر المؤهل؟"
- "ما هي متطلبات إصدار الصكوك؟"

### Follow-ups
After any response, you can ask:
- "Simplify this"
- "Give me an example"
- "وضح أكثر" (Explain more)

---

## 📁 Project Structure

```
TadqeeqAI/
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── chroma_db_v2/        # Vector database
├── bm25_index.pkl       # BM25 index
├── documents.json       # Document metadata
├── chat_history/        # Saved conversations
└── images/              # Screenshots
```

---

## 👤 Author

**Mohammed Alateegi**  
AI Graduate | Data Science Specialist

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohammed-alateegi-2853b3248/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:m7mdateegi@gmail.com)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with ❤️ for Islamic Finance Compliance</b>
</p>
