# TadqeeqAI Release Notes

---

## v1.3.0 - TadqeeqAI (Major Update)
**Release Date:** December 2024

### 🎉 Major Changes
- **Rebranded to TadqeeqAI** (تدقيق) - New name emphasizing regulatory compliance verification
- **Full Bilingual Support** - English and Arabic queries/responses
- **10x Document Expansion** - From 2 to 20 regulation documents

### ✨ New Features

#### Bilingual Support
- Query in English or Arabic - responses match your language
- RTL (Right-to-Left) text rendering for Arabic content
- Arabic source citations displayed correctly
- Bilingual example queries in sidebar

#### New Regulations Added
**CMA (6 documents, English + Arabic):**
- Capital Market Institutions Regulations
- Capital Market Law
- Glossary of Defined Terms
- Investment Funds Regulations
- Law of Systemically Important Financial Institutions
- Merger and Acquisition Regulations

**SAMA (4 documents, English + Arabic):**
- Finance Companies Control Law
- Implementing Regulation of the Finance Companies Control Law
- Real Estate Finance Law
- Implementing Regulation of the Real Estate Finance Law

#### Performance Improvements
- **GPU Acceleration** - iGPU support via Intel workaround
- **4x Faster Queries** - From ~1:45 average to ~17 seconds
- **Smart Model Offloading** - Automatic unload after 5 minutes idle (saves RAM)

#### UI Enhancements
- Text selection enabled in chat messages
- Markdown formatting rendered (bold, headers, lists)
- Disclaimer footer added
- Language indicator badges
- Improved source citation display with language markers

### 🔧 Technical Changes
- Switched to multilingual embedding model (`paraphrase-multilingual-MiniLM-L12-v2`)
- All documents converted to clean Markdown format
- Article-aware chunking for better retrieval
- Fresh ChromaDB architecture with bilingual metadata

### 📁 Project Structure
```
TadqeeqAI/
├── main.py                 # Main application
├── build_embeddings.py     # Embedding generator
├── rag_pipeline.py         # RAG logic
├── data/
│   ├── CMA/
│   │   ├── en/            # 6 English docs
│   │   └── ar/            # 6 Arabic docs
│   └── SAMA/
│       ├── en/            # 4 English docs
│       └── ar/            # 4 Arabic docs
└── chroma_db/             # Vector database
```

---

## v1.2.0 - ShariaGuide Stable
**Release Date:** November 2024

### ✨ Features
- Stable SAMA regulations support
- Single-regulator RAG system
- Desktop application with PyWebView
- Query expansion for better retrieval
- Source citations with article references

### 📊 Coverage
- **SAMA:** Finance Companies Control Law (142 articles)
  - Implementing Regulation of the Finance Companies Control Law

### ⚡ Performance
- Average query time: ~13 seconds (CPU-only)
- Embedding model: `all-MiniLM-L6-v2`
- LLM: Qwen 2.5 7B via Ollama

### 🎨 UI
- Clean dark theme with green accents
- Sidebar with example queries
- Loading animations
- Source display panel

---

## v1.1.0 - Initial Release
**Release Date:** October 2024

### ✨ Features
- Basic RAG implementation for SAMA regulations
- Command-line interface
- Simple query-response system

### 📊 Coverage
- **SAMA:** Finance Companies Control Law only

### 🔧 Technical
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- Ollama for local LLM inference

---

## Installation

### Prerequisites
- Python 3.10+
- Ollama with `qwen2.5:7b` model
- 8GB+ RAM recommended

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/TadqeeqAI.git
cd TadqeeqAI

# Install dependencies
pip install -r requirements.txt

# Build embeddings (first time only)
python build_embeddings.py

# Run application
python main.py
```

### GPU Acceleration (Optional)
For Intel iGPU acceleration, set environment variables before running:
```bash
# Windows PowerShell
$env:OLLAMA_INTEL_GPU = "1"

# Linux/Mac
export OLLAMA_INTEL_GPU=1
```

---

## Requirements

```
chromadb>=0.4.0
sentence-transformers>=2.2.0
ollama>=0.1.0
pywebview>=4.0.0
```

---

## License
MIT License - See LICENSE file for details.

---

## Credits
Developed for Tarmeez Capital by Mohammed
