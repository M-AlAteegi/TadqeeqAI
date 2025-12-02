"""
ShariaGuide - Desktop Application
==================================
A standalone desktop app for Islamic Finance regulatory compliance.

Double-click to run - opens in its own window like a real app.

REQUIREMENTS:
    pip install pywebview flask sentence-transformers chromadb requests

USAGE:
    python ShariaGuide.py
"""

import webview
import threading
import json
import chromadb
from sentence_transformers import SentenceTransformer
import requests


# ============================================================
# RAG SYSTEM
# ============================================================

class ShariaGuideRAG:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        print("Loading ShariaGuide RAG system...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_collection("sharia_guide")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "qwen2.5:7b"
        print(f"Ready! {self.collection.count()} documents indexed.")
    
    def retrieve(self, query, n_results=5):
        query_embedding = self.embedding_model.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        
        retrieved = []
        for i in range(len(results['documents'][0])):
            retrieved.append({
                "chunk_id": results['metadatas'][0][i]['chunk_id'],
                "source": results['metadatas'][0][i]['source'],
                "text": results['documents'][0][i]
            })
        return retrieved
    
    def generate_prompt(self, query, context_docs):
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            source_short = doc['source'].replace('.pdf', '').replace('_', ' ')
            context_parts.append(
                f"[DOCUMENT {i}]\nSource: {source_short}\nArticle: {doc['chunk_id']}\nContent:\n{doc['text']}"
            )
        
        context = "\n\n" + "="*50 + "\n\n".join(context_parts)
        
        prompt = f"""You are ShariaGuide, a Saudi Arabian regulatory compliance assistant specialized in Islamic finance laws.

YOUR TASK: Answer the user's question using ONLY the regulatory documents provided below. 

STRICT RULES:
1. ONLY use information from the provided documents - do not use external knowledge
2. For every fact you state, cite the specific Article number (e.g., "According to Article 10...")
3. If the documents contain a list, reproduce it accurately
4. If the answer is not in the documents, say "This information is not available in the provided regulatory documents"
5. Be precise with numbers, fees, and requirements - quote them exactly as written
6. Keep your answer focused and professional

REGULATORY DOCUMENTS:
{context}

{"="*50}

USER QUESTION: {query}

YOUR ANSWER (cite all sources):"""
        
        return prompt
    
    def query(self, question):
        docs = self.retrieve(question, n_results=3)
        prompt = self.generate_prompt(question, docs)
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 1000,
                        "top_p": 0.9
                    }
                },
                timeout=180
            )
            
            if response.status_code == 200:
                answer = response.json()['response']
            else:
                answer = f"Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            answer = "Error: Cannot connect to Ollama. Make sure Ollama is running."
        except Exception as e:
            answer = f"Error: {str(e)}"
        
        sources = [{"article": d['chunk_id'], "source": d['source'].replace('.pdf', '').replace('_', ' ')} for d in docs]
        
        return {"answer": answer, "sources": sources}


# ============================================================
# API CLASS FOR PYWEBVIEW
# ============================================================

class API:
    """API exposed to JavaScript in the webview."""
    
    def __init__(self):
        self.rag = None
    
    def initialize(self):
        """Initialize the RAG system."""
        try:
            self.rag = ShariaGuideRAG.get_instance()
            return {"status": "ready", "count": self.rag.collection.count()}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query(self, question):
        """Process a question through the RAG system."""
        if not self.rag:
            return {"answer": "System not initialized. Please restart the application.", "sources": []}
        
        try:
            result = self.rag.query(question)
            return result
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": []}


# ============================================================
# HTML INTERFACE
# ============================================================

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShariaGuide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0f0d;
            --bg-secondary: #111916;
            --bg-tertiary: #1a2420;
            --bg-hover: #243029;
            --accent-primary: #22c55e;
            --accent-secondary: #16a34a;
            --accent-glow: rgba(34, 197, 94, 0.15);
            --text-primary: #f0fdf4;
            --text-secondary: #a3a3a3;
            --text-muted: #6b7280;
            --border-color: #2a3631;
            --user-bubble: #1e3a2f;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 18px;
            color: var(--bg-primary);
            box-shadow: 0 4px 20px var(--accent-glow);
        }

        .logo-text {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .logo-subtitle {
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 2px;
        }

        .new-chat-btn {
            margin: 20px;
            padding: 14px 20px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s ease;
        }

        .new-chat-btn:hover {
            background: var(--bg-hover);
            border-color: var(--accent-primary);
        }

        .sidebar-section {
            padding: 20px;
            flex: 1;
            overflow-y: auto;
        }

        .section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }

        .example-query {
            padding: 12px 14px;
            background: var(--bg-tertiary);
            border-radius: 10px;
            margin-bottom: 8px;
            font-size: 13px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }

        .example-query:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
            border-color: var(--border-color);
        }

        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid var(--border-color);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--text-muted);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .status-dot.loading {
            background: #f59e0b;
        }

        .status-dot.error {
            background: #ef4444;
            animation: none;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Main Chat Area */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .chat-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            -webkit-app-region: drag;
        }

        .model-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: var(--bg-tertiary);
            border-radius: 20px;
            font-size: 13px;
            color: var(--text-secondary);
            -webkit-app-region: no-drag;
        }

        .model-badge .dot {
            width: 6px;
            height: 6px;
            background: var(--accent-primary);
            border-radius: 50%;
        }

        /* Chat Messages */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            scroll-behavior: smooth;
        }

        .welcome-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            padding: 40px;
        }

        .welcome-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            font-weight: 700;
            color: var(--bg-primary);
            margin-bottom: 24px;
            box-shadow: 0 8px 40px var(--accent-glow);
        }

        .welcome-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }

        .welcome-subtitle {
            font-size: 16px;
            color: var(--text-secondary);
            max-width: 500px;
            line-height: 1.6;
        }

        .message {
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: var(--user-bubble);
            color: var(--accent-primary);
        }

        .message.assistant .message-avatar {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: var(--bg-primary);
        }

        .message-content {
            flex: 1;
            min-width: 0;
        }

        .message-role {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text-primary);
        }

        .message-text {
            font-size: 15px;
            line-height: 1.7;
            color: var(--text-secondary);
            white-space: pre-wrap;
        }

        .message.user .message-text {
            color: var(--text-primary);
        }

        .sources-container {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }

        .sources-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            margin-bottom: 10px;
        }

        .source-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 12px;
            color: var(--text-secondary);
            margin-right: 8px;
            margin-bottom: 8px;
        }

        .source-tag .article {
            color: var(--accent-primary);
            font-weight: 600;
        }

        /* Loading Animation */
        .loading-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-muted);
            font-size: 14px;
        }

        .loading-dots {
            display: flex;
            gap: 4px;
        }

        .loading-dots span {
            width: 6px;
            height: 6px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* Input Area */
        .input-area {
            padding: 20px 24px 24px;
            background: var(--bg-primary);
            border-top: 1px solid var(--border-color);
        }

        .input-container {
            max-width: 900px;
            margin: 0 auto;
            position: relative;
        }

        .input-wrapper {
            display: flex;
            align-items: flex-end;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 8px;
            transition: all 0.2s ease;
        }

        .input-wrapper:focus-within {
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 4px var(--accent-glow);
        }

        #user-input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 15px;
            padding: 10px 16px;
            resize: none;
            max-height: 200px;
            line-height: 1.5;
        }

        #user-input::placeholder {
            color: var(--text-muted);
        }

        #user-input:disabled {
            opacity: 0.5;
        }

        .send-btn {
            width: 44px;
            height: 44px;
            background: var(--accent-primary);
            border: none;
            border-radius: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .send-btn:hover:not(:disabled) {
            background: var(--accent-secondary);
            transform: scale(1.05);
        }

        .send-btn:disabled {
            background: var(--bg-tertiary);
            cursor: not-allowed;
            transform: none;
        }

        .send-btn svg {
            width: 20px;
            height: 20px;
            fill: none;
            stroke: var(--bg-primary);
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .input-footer {
            text-align: center;
            margin-top: 12px;
            font-size: 12px;
            color: var(--text-muted);
        }

        /* Init Screen */
        .init-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--bg-primary);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .init-overlay.hidden {
            display: none;
        }

        .init-spinner {
            width: 60px;
            height: 60px;
            border: 3px solid var(--border-color);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 24px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .init-text {
            font-size: 16px;
            color: var(--text-secondary);
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-muted);
        }
    </style>
</head>
<body>
    <!-- Init Overlay -->
    <div class="init-overlay" id="init-overlay">
        <div class="init-spinner"></div>
        <div class="init-text">Loading ShariaGuide...</div>
    </div>

    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <div class="logo-icon">SG</div>
                <div>
                    <div class="logo-text">ShariaGuide</div>
                    <div class="logo-subtitle">Regulatory AI</div>
                </div>
            </div>
        </div>
        
        <button class="new-chat-btn" id="new-chat-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            New Chat
        </button>
        
        <div class="sidebar-section">
            <div class="section-title">Example Queries</div>
            <div class="example-query" data-query="What are the licensing fees for finance companies?">
                What are the licensing fees for finance companies?
            </div>
            <div class="example-query" data-query="What activities can a finance company engage in?">
                What activities can a finance company engage in?
            </div>
            <div class="example-query" data-query="What is the minimum capital requirement?">
                What is the minimum capital requirement?
            </div>
            <div class="example-query" data-query="What are the penalties for violations?">
                What are the penalties for violations?
            </div>
        </div>
        
        <div class="sidebar-footer">
            <div class="status-badge">
                <div class="status-dot" id="status-dot"></div>
                <span id="status-text">Initializing...</span>
            </div>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="main">
        <header class="chat-header">
            <div class="model-badge">
                <span class="dot"></span>
                <span>Qwen2.5:7b · RAG Enabled</span>
            </div>
        </header>

        <div class="chat-container" id="chat-container">
            <div class="welcome-screen" id="welcome-screen">
                <div class="welcome-icon">SG</div>
                <h1 class="welcome-title">Welcome to ShariaGuide</h1>
                <p class="welcome-subtitle">
                    Your AI-powered assistant for Saudi Arabian Islamic finance regulations. 
                    Ask questions about licensing, compliance, capital requirements, and more.
                </p>
            </div>
        </div>

        <div class="input-area">
            <div class="input-container">
                <div class="input-wrapper">
                    <textarea 
                        id="user-input" 
                        placeholder="Ask about Saudi finance regulations..." 
                        rows="1"
                        disabled
                    ></textarea>
                    <button class="send-btn" id="send-btn" disabled>
                        <svg viewBox="0 0 24 24">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
                <div class="input-footer">
                    ShariaGuide retrieves from official regulatory documents · Responses include source citations
                </div>
            </div>
        </div>
    </main>

    <script>
        // Elements
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const welcomeScreen = document.getElementById('welcome-screen');
        const initOverlay = document.getElementById('init-overlay');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const newChatBtn = document.getElementById('new-chat-btn');
        const exampleQueries = document.querySelectorAll('.example-query');
        
        let isLoading = false;
        let isReady = false;

        // Initialize the app
        async function initialize() {
            try {
                const result = await window.pywebview.api.initialize();
                if (result.status === 'ready') {
                    isReady = true;
                    statusDot.classList.remove('loading');
                    statusText.textContent = `Qwen2.5 · ${result.count} documents indexed`;
                    userInput.disabled = false;
                    sendBtn.disabled = false;
                    initOverlay.classList.add('hidden');
                    userInput.focus();
                } else {
                    throw new Error(result.message);
                }
            } catch (error) {
                statusDot.classList.add('error');
                statusText.textContent = 'Error: ' + error.message;
                initOverlay.querySelector('.init-text').textContent = 'Error loading system: ' + error.message;
            }
        }

        // Wait for pywebview to be ready
        window.addEventListener('pywebviewready', function() {
            initialize();
        });

        // Auto-resize textarea
        function autoResize() {
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
        }

        userInput.addEventListener('input', autoResize);

        // Handle Enter key
        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Send button click
        sendBtn.addEventListener('click', sendMessage);

        // New chat button
        newChatBtn.addEventListener('click', function() {
            chatContainer.innerHTML = `
                <div class="welcome-screen" id="welcome-screen">
                    <div class="welcome-icon">SG</div>
                    <h1 class="welcome-title">Welcome to ShariaGuide</h1>
                    <p class="welcome-subtitle">
                        Your AI-powered assistant for Saudi Arabian Islamic finance regulations. 
                        Ask questions about licensing, compliance, capital requirements, and more.
                    </p>
                </div>
            `;
        });

        // Example queries
        exampleQueries.forEach(function(el) {
            el.addEventListener('click', function() {
                const query = this.getAttribute('data-query');
                userInput.value = query;
                autoResize();
                sendMessage();
            });
        });

        // Add message to chat
        function addMessage(role, content, sources) {
            // Hide welcome screen
            const welcome = document.getElementById('welcome-screen');
            if (welcome) welcome.style.display = 'none';

            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + role;
            
            const avatar = role === 'user' ? 'You' : 'SG';
            const roleName = role === 'user' ? 'You' : 'ShariaGuide';
            
            let sourcesHtml = '';
            if (sources && sources.length > 0) {
                let tags = '';
                sources.forEach(function(s) {
                    const shortSource = s.source.length > 35 ? s.source.substring(0, 35) + '...' : s.source;
                    tags += '<span class="source-tag"><span class="article">' + s.article + '</span> · ' + shortSource + '</span>';
                });
                sourcesHtml = '<div class="sources-container"><div class="sources-title">Sources Referenced</div>' + tags + '</div>';
            }

            messageDiv.innerHTML = 
                '<div class="message-avatar">' + avatar + '</div>' +
                '<div class="message-content">' +
                    '<div class="message-role">' + roleName + '</div>' +
                    '<div class="message-text">' + escapeHtml(content) + '</div>' +
                    sourcesHtml +
                '</div>';

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Escape HTML
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Add loading message
        function addLoadingMessage() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant';
            messageDiv.id = 'loading-message';
            
            messageDiv.innerHTML = 
                '<div class="message-avatar">SG</div>' +
                '<div class="message-content">' +
                    '<div class="message-role">ShariaGuide</div>' +
                    '<div class="loading-indicator">' +
                        '<div class="loading-dots"><span></span><span></span><span></span></div>' +
                        '<span>Searching regulatory documents...</span>' +
                    '</div>' +
                '</div>';

            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Remove loading message
        function removeLoadingMessage() {
            const loading = document.getElementById('loading-message');
            if (loading) loading.remove();
        }

        // Send message
        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message || isLoading || !isReady) return;

            isLoading = true;
            sendBtn.disabled = true;
            userInput.disabled = true;
            userInput.value = '';
            userInput.style.height = 'auto';

            addMessage('user', message, null);
            addLoadingMessage();

            try {
                const result = await window.pywebview.api.query(message);
                removeLoadingMessage();
                addMessage('assistant', result.answer, result.sources);
            } catch (error) {
                removeLoadingMessage();
                addMessage('assistant', 'An error occurred: ' + error.message, null);
            }

            isLoading = false;
            sendBtn.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    </script>
</body>
</html>
'''


# ============================================================
# MAIN - RUN THE DESKTOP APP
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   SHARIAGUIDE DESKTOP APP")
    print("="*50 + "\n")
    
    api = API()
    
    # Create the window
    window = webview.create_window(
        title='ShariaGuide - Islamic Finance Compliance',
        html=HTML,
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 700),
        background_color='#0a0f0d'
    )
    
    # Start the app
    webview.start(debug=False)
