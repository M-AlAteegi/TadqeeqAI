# TadqeeqAI v2.2 Release Notes

## 🎉 What's New

### 📄 Document Analysis
- **Upload & Analyze**: Upload PDF or DOCX files (up to 50 pages) directly into the app
- **Drag & Drop**: Simply drag files onto the app window
- **Smart Parsing**: Automatic text extraction with Arabic language detection

### ✅ Compliance Checker
- **Automated Scanning**: One-click regulatory compliance analysis
- **6 Categories**: Capital requirements, licensing, disclosure, governance, AML/KYC, Sharia compliance
- **Visual Report**: Clear compliance score with detailed findings

### 📥 Chat Export
- **Markdown Export**: Save conversations as `.md` files
- **PDF Export**: Professional PDF output with formatting preserved
- **Native File Dialog**: Standard Windows save dialog for file location

### 💅 UI Improvements
- **Gemini-Style Input Bar**: Modern design with bilateral button layout
- **Attach Button**: Quick file upload via 📎 button
- **In-App Notifications**: Error and success messages within the app (no more Windows popups)
- **AI Disclaimer**: Helpful reminder that AI can make mistakes

### 🔧 Under the Hood
- **Hidden Ollama**: LLM server runs completely hidden (no system tray icon)
- **Auto-Cleanup**: Ollama automatically stops when app closes
- **Better Error Handling**: Improved stability and error messages

---

## 📦 New Dependencies

```bash
pip install PyMuPDF python-docx reportlab
```

---

## 🐛 Bug Fixes
- Fixed welcome screen stats not showing after deleting all chats
- Fixed duplicate input elements in HTML
- Improved Ollama process management on Windows

---

## 📋 Requirements
- Python 3.12+
- Ollama with `aya:8b` model
- 8GB+ RAM recommended

---

## 🚀 Upgrade Instructions

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install PyMuPDF python-docx reportlab

# Run the app
python main.py
```

---

## 📸 Screenshots

See the updated [README](README.md) for new screenshots showcasing document analysis.

---

**Full Changelog**: https://github.com/M-AlAteegi/TadqeeqAI/compare/v2.1...v2.2
