"""
TadqeeqAI v2.1
==============
Bilingual RAG system for Saudi Arabian financial regulations.
SAMA + CMA · English + Arabic

v2.1 Features:
- Chat history with persistent storage
- New Chat button
- Improved prompts with dynamic closings
- Follow-up support (simplify, examples)
- Domain-restricted responses
- Auto-start Ollama (Intel ipex-llm)

Prerequisites:
    1. Ensure chroma_db_v2 and bm25_index.pkl exist
    2. Ollama will be started automatically
"""

import json
import pickle
import re
import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import ollama
import numpy as np
import webview

# Configuration
CHROMA_PATH = "./chroma_db_v2"
BM25_PATH = "./bm25_index.pkl"
DOCS_PATH = "./documents.json"
CHAT_HISTORY_PATH = "./chat_history"
EMBEDDING_MODEL = 'intfloat/multilingual-e5-base'

# LLM Model Options:
# - 'aya:8b'       : Best for Arabic, no Chinese leak, follows instructions well
# - 'qwen2.5:7b'   : Good overall but leaks Chinese on long Arabic responses  
# - 'jais:13b'     : Arabic-first but truncates responses
LLM_MODEL = 'aya:8b'

# Ensure chat history directory exists
Path(CHAT_HISTORY_PATH).mkdir(exist_ok=True)


def start_ollama():
    """Start Ollama server if not already running."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("  ✓ Ollama is already running")
            return True
    except:
        pass
    
    print("  Starting Ollama...")
    try:
        # On Windows, use START /B to run in background without blocking
        if os.name == 'nt':
            subprocess.Popen(
                'start /B ollama serve',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        for i in range(30):
            time.sleep(1)
            try:
                result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    print("  ✓ Ollama started successfully")
                    return True
            except:
                pass
            if i % 10 == 9:
                print(f"    Waiting... ({i+1}s)")
        
        print("  ⚠ Ollama may not have started - continuing anyway")
        return False
    except Exception as e:
        print(f"  ⚠ Could not start Ollama: {e}")
        return False


class ChatHistory:
    """Manages persistent chat history."""
    
    def __init__(self):
        self.history_path = Path(CHAT_HISTORY_PATH)
        self.current_chat_id = None
        self.current_messages = []
    
    def new_chat(self):
        """Start a new chat session."""
        self.current_chat_id = str(uuid.uuid4())[:8]
        self.current_messages = []
        return self.current_chat_id
    
    def add_message(self, role, content, sources=None, regulator=None):
        """Add a message to current chat."""
        msg = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        if sources:
            msg['sources'] = sources
        if regulator:
            msg['regulator'] = regulator
        self.current_messages.append(msg)
        self._save_current()
    
    def _save_current(self):
        """Save current chat to file."""
        if not self.current_chat_id:
            return
        filepath = self.history_path / f"{self.current_chat_id}.json"
        chat_data = {
            'id': self.current_chat_id,
            'created': self.current_messages[0]['timestamp'] if self.current_messages else datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'messages': self.current_messages,
            'preview': self._get_preview()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
    
    def _get_preview(self):
        """Get first user message as preview."""
        for msg in self.current_messages:
            if msg['role'] == 'user':
                text = msg['content']
                return text[:50] + '...' if len(text) > 50 else text
        return 'New Chat'
    
    def get_recent_chats(self, limit=20):
        """Get list of recent chats."""
        chats = []
        for filepath in sorted(self.history_path.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chats.append({
                        'id': data['id'],
                        'preview': data.get('preview', 'Chat'),
                        'updated': data.get('updated', ''),
                        'message_count': len(data.get('messages', []))
                    })
            except:
                pass
            if len(chats) >= limit:
                break
        return chats
    
    def load_chat(self, chat_id):
        """Load a specific chat."""
        filepath = self.history_path / f"{chat_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.current_chat_id = chat_id
                self.current_messages = data.get('messages', [])
                return self.current_messages
        return []
    
    def get_conversation_context(self, limit=6):
        """Get recent messages for context (for follow-ups)."""
        return self.current_messages[-limit:] if self.current_messages else []
    
    def delete_chat(self, chat_id):
        """Delete a chat permanently."""
        filepath = self.history_path / f"{chat_id}.json"
        if filepath.exists():
            filepath.unlink()
            # If we deleted the current chat, reset
            if self.current_chat_id == chat_id:
                self.current_chat_id = None
                self.current_messages = []
            return True
        return False


class TadqeeqRAG:
    """Hybrid RAG system with BM25 + semantic search."""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        print("Loading TadqeeqAI v2.1...")
        
        # Start Ollama first
        start_ollama()
        
        # Load documents
        print("  Loading documents...")
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        # Count by regulator/language
        self.stats = {'SAMA': {'en': 0, 'ar': 0}, 'CMA': {'en': 0, 'ar': 0}}
        for doc in self.documents:
            reg = doc.get('regulator', 'CMA')
            lang = doc.get('language', 'en')
            self.stats[reg][lang] += 1
        
        self.sama_count = self.stats['SAMA']['en'] + self.stats['SAMA']['ar']
        self.cma_count = self.stats['CMA']['en'] + self.stats['CMA']['ar']
        self.total = len(self.documents)
        
        print(f"    ✓ {self.total} articles (SAMA: {self.sama_count}, CMA: {self.cma_count})")
        
        # Load BM25 index
        print("  Loading BM25 index...")
        with open(BM25_PATH, 'rb') as f:
            self.bm25 = pickle.load(f)
        print("    ✓ BM25 ready")
        
        # Load embedding model
        print("  Loading embedding model...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        print(f"    ✓ {EMBEDDING_MODEL}")
        
        # Connect to ChromaDB
        print("  Connecting to ChromaDB...")
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = self.client.get_collection("tadqeeq_v2")
        print(f"    ✓ {self.collection.count()} documents")
        
        # Warm up LLM
        print("  Loading LLM...")
        self._warmup_llm()
        print(f"    ✓ {LLM_MODEL}")
        
        # Chat history
        self.chat_history = ChatHistory()
        
        print("\n✓ TadqeeqAI v2.1 Ready!\n")
    
    def _warmup_llm(self):
        try:
            ollama.generate(model=LLM_MODEL, prompt="test", options={"num_predict": 1})
        except:
            print(f"      Pulling {LLM_MODEL}...")
            ollama.pull(LLM_MODEL)
    
    def detect_language(self, text):
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    
    def detect_regulator(self, query):
        q_lower = query.lower()
        
        # English keywords
        sama_en = ['sama', 'finance company', 'finance companies', 'financing company',
                   'licensing fee', 'real estate finance', 'mortgage', 'microfinance',
                   'finance control', 'monetary authority', 'bank', 'banking']
        cma_en = ['cma', 'capital market', 'securities', 'sukuk', 'debt instrument',
                  'investment fund', 'qualified investor', 'public offering', 'ipo',
                  'private placement', 'prospectus', 'listing', 'merger', 'acquisition',
                  'stock', 'shares', 'exchange']
        
        # Arabic keywords (don't lowercase)
        sama_ar = ['ساما', 'شركة التمويل', 'شركات التمويل', 'رسوم الترخيص', 'التمويل العقاري',
                   'التمويل الأصغر', 'مؤسسة النقد', 'البنك المركزي', 'تمويل']
        cma_ar = ['مستثمر مؤهل', 'المستثمر المؤهل', 'هيئة السوق المالية', 'هيئة السوق',
                  'صكوك', 'الصكوك', 'طرح عام', 'طرح خاص', 'نشرة الإصدار',
                  'صناديق الاستثمار', 'أوراق مالية', 'الأوراق المالية', 'سوق المال',
                  'الاندماج', 'الاستحواذ', 'الأسهم', 'التداول']
        
        # Check English keywords
        sama_match = any(kw in q_lower for kw in sama_en)
        cma_match = any(kw in q_lower for kw in cma_en)
        
        # Check Arabic keywords (case-sensitive)
        sama_match = sama_match or any(kw in query for kw in sama_ar)
        cma_match = cma_match or any(kw in query for kw in cma_ar)
        
        if sama_match and cma_match:
            return 'BOTH'
        elif sama_match:
            return 'SAMA'
        elif cma_match:
            return 'CMA'
        return 'BOTH'
    
    def translate_arabic_query(self, query):
        """Translate Arabic query keywords to English for searching English documents."""
        translations = {
            'رسوم الترخيص': 'licensing fees',
            'رسوم ترخيص': 'licensing fees',
            'شركات التمويل': 'finance companies',
            'شركة التمويل': 'finance company',
            'التمويل العقاري': 'real estate finance',
            'التمويل الأصغر': 'microfinance',
            'المستثمر المؤهل': 'qualified investor',
            'مستثمر مؤهل': 'qualified investor',
            'الصكوك': 'sukuk debt instruments',
            'صكوك': 'sukuk debt instruments',
            'أدوات الدين': 'debt instruments',
            'طرح عام': 'public offering',
            'طرح خاص': 'private placement',
            'نشرة الإصدار': 'prospectus',
            'صناديق الاستثمار': 'investment funds',
            'صندوق استثمار': 'investment fund',
            'رأس المال': 'capital requirements',
            'متطلبات رأس المال': 'capital requirements',
            'الحد الأدنى': 'minimum requirements',
            'هيئة السوق المالية': 'capital market authority CMA',
            'مؤسسة النقد': 'SAMA monetary authority',
            'ساما': 'SAMA',
            'الاندماج': 'merger',
            'الاستحواذ': 'acquisition',
            'الأسهم': 'shares stocks',
            'الإفصاح': 'disclosure',
            'الحوكمة': 'governance',
            'مجلس الإدارة': 'board of directors',
            'تقرير سنوي': 'annual report',
            'القوائم المالية': 'financial statements',
            'المراجع الخارجي': 'external auditor',
            'العقوبات': 'penalties',
            'المخالفات': 'violations',
            'الترخيص': 'license licensing',
            'التسجيل': 'registration',
            'الإدراج': 'listing',
            'السوق الموازية': 'parallel market',
            'الطرح': 'offering',
            'الاكتتاب': 'subscription IPO',
        }
        
        result = query
        for ar, en in translations.items():
            if ar in query:
                result = result + ' ' + en
        
        if result != query:
            return result
        
        return query
    
    def expand_query(self, query, lang):
        q = query.lower()
        mappings = {
            'sukuk': 'debt instruments securities bonds',
            'sukuk issuance': 'debt instruments offering securities',
            'debt instruments': 'sukuk securities bonds',
            'licensing fee': 'license fee financial consideration',
            'licensing fees': 'license fee financial consideration',
            'qualified investor': 'accredited investor',
            'capital requirements': 'minimum capital paid up capital',
            'finance company': 'finance companies',
            'microfinance': 'micro finance small finance',
            'real estate finance': 'mortgage property finance',
            'investment fund': 'investment funds',
            'public offering': 'IPO offering securities',
            'private placement': 'exempt offering',
        }
        expansions = [exp for term, exp in mappings.items() if term in q]
        return query + ' ' + ' '.join(expansions) if expansions else query
    
    def bm25_search(self, query, regulator, language, top_k=15, force_english=False):
        """BM25 keyword search."""
        search_lang = 'en' if force_english else language
        tokens = re.findall(r'[\u0600-\u06FF]+|[a-zA-Z]+|\d+', query.lower())
        if not tokens: return []
        scores = self.bm25.get_scores(tokens)
        results = []
        for idx in np.argsort(scores)[::-1]:
            if len(results) >= top_k or idx >= len(self.documents): continue
            doc = self.documents[idx]
            if regulator != 'BOTH' and doc.get('regulator') != regulator: continue
            if doc.get('language') != search_lang: continue
            if scores[idx] > 0:
                results.append({'doc': doc, 'score': float(scores[idx]), 'source': 'bm25'})
        return results
    
    def semantic_search(self, query, regulator, language, top_k=15, force_english=False):
        """Semantic search."""
        search_lang = 'en' if force_english else language
        embedding = self.embedder.encode([f"query: {query}"]).tolist()
        where = {"language": {"$eq": search_lang}} if regulator == 'BOTH' else {
            "$and": [{"language": {"$eq": search_lang}}, {"regulator": {"$eq": regulator}}]}
        try:
            results = self.collection.query(query_embeddings=embedding, n_results=top_k, where=where)
        except:
            results = self.collection.query(query_embeddings=embedding, n_results=top_k * 2)
        output = []
        if results['documents'] and results['documents'][0]:
            for doc_text, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
                if regulator != 'BOTH' and meta.get('regulator') != regulator: continue
                if meta.get('language') != search_lang: continue
                output.append({'doc': {'text': doc_text, 'article': meta.get('article', ''),
                    'document': meta.get('document', ''), 'regulator': meta.get('regulator', ''),
                    'language': meta.get('language', '')}, 'score': 1/(1+dist), 'source': 'semantic'})
        return output[:top_k]
    
    def hybrid_search(self, query, n_results=5):
        """Hybrid search with English Bridge strategy."""
        user_language = self.detect_language(query)
        regulator = self.detect_regulator(query)
        
        if user_language == 'ar':
            english_query = self.translate_arabic_query(query)
            expanded = self.expand_query(english_query, 'en')
            print(f"DEBUG: Arabic Query → English Bridge")
            print(f"  Original: {query[:50]}")
            print(f"  Translated: {english_query[:50]}")
            print(f"  Regulator: {regulator}")
            bm25_res = self.bm25_search(expanded, regulator, user_language, force_english=True)
            sem_res = self.semantic_search(expanded, regulator, user_language, force_english=True)
        else:
            expanded = self.expand_query(query, user_language)
            print(f"DEBUG: English Query='{query[:50]}', Reg={regulator}")
            bm25_res = self.bm25_search(expanded, regulator, user_language)
            sem_res = self.semantic_search(expanded, regulator, user_language)
        
        print(f"DEBUG: BM25={len(bm25_res)}, Semantic={len(sem_res)}")
        
        # RRF Fusion
        doc_scores = {}
        k = 60
        for rank, r in enumerate(bm25_res):
            key = f"{r['doc']['document']}:{r['doc']['article']}"
            if key not in doc_scores: doc_scores[key] = {'doc': r['doc'], 'rrf': 0, 'src': set()}
            doc_scores[key]['rrf'] += 1/(k+rank+1)
            doc_scores[key]['src'].add('BM25')
        for rank, r in enumerate(sem_res):
            key = f"{r['doc']['document']}:{r['doc']['article']}"
            if key not in doc_scores: doc_scores[key] = {'doc': r['doc'], 'rrf': 0, 'src': set()}
            doc_scores[key]['rrf'] += 1/(k+rank+1)
            doc_scores[key]['src'].add('Semantic')
        sorted_res = sorted(doc_scores.values(), key=lambda x: x['rrf'], reverse=True)
        final = []
        for r in sorted_res[:n_results]:
            final.append(r['doc'])
            print(f"  → {r['doc']['article']} [{'+'.join(r['src'])}]")
        return final, regulator, user_language
    
    def is_follow_up(self, query):
        """Detect if query is a follow-up request."""
        query_lower = query.lower().strip()
        
        # English follow-up patterns
        follow_up_en = [
            'yes', 'yeah', 'sure', 'please', 'ok', 'okay',
            'simplify', 'explain', 'example', 'examples', 'scenario',
            'more details', 'elaborate', 'clarify', 'what do you mean',
            'can you explain', 'help me understand', 'break it down',
            'in simple terms', 'simpler', 'easier'
        ]
        
        # Arabic follow-up patterns
        follow_up_ar = [
            'نعم', 'أجل', 'طيب', 'حسنا', 'موافق', 'تمام',
            'وضح', 'اشرح', 'مثال', 'أمثلة', 'سيناريو',
            'تفاصيل أكثر', 'بسط', 'بشكل أبسط', 'ساعدني أفهم',
            'ماذا تعني', 'اشرح أكثر'
        ]
        
        if any(pattern in query_lower for pattern in follow_up_en):
            return True
        if any(pattern in query for pattern in follow_up_ar):
            return True
        
        # Very short responses are likely follow-ups
        if len(query.strip()) < 15 and len(query.split()) <= 3:
            return True
        
        return False
    
    def is_out_of_domain(self, query):
        """Check if query is outside SAMA/CMA domain."""
        query_lower = query.lower()
        
        # Out of domain indicators
        out_of_domain = [
            'weather', 'recipe', 'cook', 'movie', 'song', 'music',
            'game', 'sport', 'football', 'soccer', 'basketball',
            'joke', 'story', 'poem', 'write me', 'create a',
            'translate', 'what is the capital', 'who is the president',
            'how to code', 'python', 'javascript', 'programming',
            'health', 'medical', 'doctor', 'disease',
            'travel', 'hotel', 'flight', 'vacation',
            'الطقس', 'وصفة', 'طبخ', 'فيلم', 'أغنية', 'موسيقى',
            'لعبة', 'رياضة', 'كرة القدم', 'نكتة', 'قصة', 'قصيدة',
            'ترجم', 'عاصمة', 'رئيس', 'برمجة', 'صحة', 'طبيب', 'سفر'
        ]
        
        # Check for out-of-domain content
        if any(term in query_lower for term in out_of_domain):
            return True
        
        return False
    
    def build_prompt(self, question, docs, language, is_follow_up=False, conversation_context=None):
        """Build LLM prompt optimized for Aya model."""
        ctx = "\n\n---\n\n".join([f"[Document {i}]\nSource: {d['document']}\nArticle: {d['article']}\nContent:\n{d['text']}" 
                                  for i, d in enumerate(docs, 1)])
        
        # Add conversation context for follow-ups
        conv_context = ""
        if is_follow_up and conversation_context:
            conv_context = "\n\nPrevious conversation:\n"
            for msg in conversation_context[-4:]:  # Last 4 messages
                role = "User" if msg['role'] == 'user' else "Assistant"
                conv_context += f"{role}: {msg['content'][:500]}\n"
        
        if language == 'ar':
            if is_follow_up:
                return f"""أنت مساعد قانوني متخصص في الأنظمة المالية السعودية (ساما وهيئة السوق المالية).

المحادثة السابقة:
{conv_context}

المستندات المرجعية:
{ctx}

طلب المستخدم: {question}

المستخدم يطلب توضيحاً أو تبسيطاً. قم بما يلي:
- إذا طلب تبسيط: اشرح المفهوم بلغة سهلة وواضحة
- إذا طلب مثال: قدم سيناريو عملي يوضح التطبيق
- إذا طلب توضيح: اشرح النقاط الغامضة بالتفصيل

الإجابة:"""
            else:
                return f"""أنت مساعد قانوني متخصص في الأنظمة المالية السعودية (ساما وهيئة السوق المالية).

تعليمات مهمة:
- اقرأ كل مستند بعناية قبل الإجابة
- استخرج المعلومات المطلوبة من المستندات
- اذكر رقم المادة عند الاستشهاد (مثال: المادة 22)
- مصطلح "debt instruments" يعني "الصكوك" أو "أدوات الدين"
- اكتب الأرقام والمبالغ كما هي في المستند
- استخدم تنسيق Markdown: استخدم **نص** للتأكيد و - للقوائم
- إذا لم تجد المعلومة المحددة، قل ذلك بوضوح
- لا تذكر أنك ستساعد في نهاية الإجابة

المستندات المرجعية:
{ctx}

السؤال: {question}

الإجابة:"""
        
        # English prompts
        if is_follow_up:
            return f"""You are a legal assistant specializing in Saudi Arabian financial regulations (SAMA and CMA).

Previous conversation:
{conv_context}

Reference Documents:
{ctx}

User request: {question}

The user is asking for clarification or simplification. Do the following:
- If they want simplification: Explain the concept in plain, easy-to-understand language
- If they want examples: Provide a practical scenario showing how this applies
- If they want clarification: Explain the unclear points in detail

Answer:"""
        else:
            return f"""You are a legal assistant specializing in Saudi Arabian financial regulations (SAMA and CMA).

Important instructions:
- Read each document carefully before answering
- Extract the relevant information from the documents
- Cite the Article number when referencing information (e.g., "Article 22")
- "Sukuk" and "debt instruments" refer to the same thing
- Preserve exact numbers and amounts as written in the documents
- Use Markdown formatting: **bold** for emphasis and - for lists
- If the specific information is not found, say so clearly
- Do not offer further assistance at the end of your response

Reference Documents:
{ctx}

Question: {question}

Answer:"""
    
    def build_out_of_domain_response(self, language):
        """Return response for out-of-domain queries."""
        if language == 'ar':
            return """عذراً، أنا مساعد متخصص في الأنظمة المالية السعودية فقط.

يمكنني مساعدتك في:
- **أنظمة ساما**: شركات التمويل، التمويل العقاري، التمويل الأصغر
- **أنظمة هيئة السوق المالية**: الصكوك، صناديق الاستثمار، المستثمر المؤهل، الطرح والإدراج

يرجى طرح سؤال يتعلق بهذه المواضيع."""
        else:
            return """I apologize, but I am a specialized assistant for Saudi Arabian financial regulations only.

I can help you with:
- **SAMA regulations**: Finance companies, real estate finance, microfinance
- **CMA regulations**: Sukuk, investment funds, qualified investors, offerings and listings

Please ask a question related to these topics."""
    
    def generate_response(self, question):
        """Generate response with follow-up support."""
        lang = self.detect_language(question)
        
        # Check if out of domain
        if self.is_out_of_domain(question):
            return {
                'answer': self.build_out_of_domain_response(lang),
                'sources': [],
                'regulator': 'NONE'
            }
        
        # Check if this is a follow-up
        is_followup = self.is_follow_up(question)
        conversation_context = None
        
        if is_followup:
            conversation_context = self.chat_history.get_conversation_context()
            # If we have context, use the previous search results
            if conversation_context:
                # Find the last assistant message with sources
                last_sources = None
                for msg in reversed(conversation_context):
                    if msg['role'] == 'assistant' and 'sources' in msg:
                        last_sources = msg.get('sources', [])
                        break
        
        # Perform search
        docs, reg, lang = self.hybrid_search(question)
        
        if not docs:
            no_info = 'No relevant information found.' if lang == 'en' else 'لم يتم العثور على معلومات ذات صلة.'
            return {'answer': no_info, 'sources': [], 'regulator': reg}
        
        prompt = self.build_prompt(question, docs, lang, is_followup, conversation_context)
        resp = ollama.generate(model=LLM_MODEL, prompt=prompt, options={'temperature': 0.1, 'num_predict': 2000})
        
        seen = set()
        sources = [{'article': d['article'], 'document': d['document']} for d in docs if d['article'] not in seen and not seen.add(d['article'])]
        
        return {'answer': resp['response'].strip(), 'sources': sources, 'regulator': reg}


class API:
    def __init__(self):
        self.rag = None
    
    def initialize(self):
        try:
            print("API.initialize() called...")
            self.rag = TadqeeqRAG.get_instance()
            print("RAG instance created successfully")
            return {
                'status': 'ready',
                'total': self.rag.total,
                'sama': self.rag.sama_count,
                'cma': self.rag.cma_count,
                'sama_en': self.rag.stats['SAMA']['en'],
                'sama_ar': self.rag.stats['SAMA']['ar'],
                'cma_en': self.rag.stats['CMA']['en'],
                'cma_ar': self.rag.stats['CMA']['ar'],
                'chats': self.rag.chat_history.get_recent_chats()
            }
        except Exception as e:
            print(f"API.initialize() ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
    
    def query(self, question):
        if not self.rag:
            self.rag = TadqeeqRAG.get_instance()
        
        # Add user message to history
        self.rag.chat_history.add_message('user', question)
        
        # Generate response
        result = self.rag.generate_response(question)
        
        # Add assistant message to history
        self.rag.chat_history.add_message(
            'assistant',
            result['answer'],
            result.get('sources'),
            result.get('regulator')
        )
        
        return result
    
    def new_chat(self):
        if not self.rag:
            self.rag = TadqeeqRAG.get_instance()
        chat_id = self.rag.chat_history.new_chat()
        return {'id': chat_id, 'chats': self.rag.chat_history.get_recent_chats()}
    
    def load_chat(self, chat_id):
        if not self.rag:
            self.rag = TadqeeqRAG.get_instance()
        messages = self.rag.chat_history.load_chat(chat_id)
        return {'messages': messages}
    
    def get_chats(self):
        if not self.rag:
            self.rag = TadqeeqRAG.get_instance()
        return {'chats': self.rag.chat_history.get_recent_chats()}
    
    def delete_chat(self, chat_id):
        if not self.rag:
            self.rag = TadqeeqRAG.get_instance()
        success = self.rag.chat_history.delete_chat(chat_id)
        return {'success': success, 'chats': self.rag.chat_history.get_recent_chats()}


HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TadqeeqAI v2.1</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --bg: #0a0d10;
            --bg2: #0f1318;
            --bg3: #161b22;
            --bg4: #1c2128;
            --border: #30363d;
            --text: #e6edf3;
            --text2: #8b949e;
            --text3: #6e7681;
            --accent: #00d4aa;
            --accent2: #00b894;
            --sama: #58a6ff;
            --cma: #3fb950;
            --danger: #f85149;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            -webkit-user-select: none;
            user-select: none;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text3); }
        
        ::selection { background: var(--accent); color: var(--bg); }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: var(--bg2);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }
        .sidebar-header {
            padding: 16px;
            border-bottom: 1px solid var(--border);
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .logo-icon {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .logo-icon svg { width: 20px; height: 20px; fill: var(--bg); }
        .logo-text { font-size: 17px; font-weight: 700; letter-spacing: -0.3px; }
        .logo-sub { font-size: 10px; color: var(--text3); margin-top: 2px; letter-spacing: 0.5px; }
        
        /* New Chat Button */
        .new-chat-btn {
            width: 100%;
            padding: 10px 14px;
            background: var(--bg3);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s ease;
        }
        .new-chat-btn:hover {
            background: var(--bg4);
            border-color: var(--accent);
        }
        .new-chat-btn svg { width: 16px; height: 16px; stroke: var(--accent); fill: none; }
        
        /* Chat History */
        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }
        .history-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text3);
            margin-bottom: 8px;
            font-weight: 600;
            padding: 0 4px;
        }
        .history-item {
            display: flex;
            align-items: center;
            padding: 8px 10px;
            background: transparent;
            border-radius: 8px;
            margin-bottom: 4px;
            font-size: 12px;
            color: var(--text2);
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
            position: relative;
        }
        .history-item:hover {
            background: var(--bg3);
            color: var(--text);
        }
        .history-item.active {
            background: var(--bg4);
            border-color: var(--border);
            color: var(--text);
        }
        .history-item-text {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .history-item-menu {
            opacity: 0;
            width: 24px;
            height: 24px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.15s ease;
            flex-shrink: 0;
        }
        .history-item:hover .history-item-menu { opacity: 1; }
        .history-item-menu:hover { background: var(--bg4); }
        .history-item-menu svg { width: 14px; height: 14px; fill: var(--text3); }
        
        /* Dropdown Menu */
        .dropdown {
            position: absolute;
            right: 0;
            top: 100%;
            background: var(--bg3);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 4px;
            z-index: 100;
            display: none;
            min-width: 120px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }
        .dropdown.show { display: block; }
        .dropdown-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            font-size: 12px;
            color: var(--danger);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .dropdown-item:hover { background: var(--bg4); }
        .dropdown-item svg { width: 14px; height: 14px; stroke: currentColor; fill: none; }
        
        /* Delete Confirmation Modal */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 200;
        }
        .modal-overlay.show { display: flex; }
        .modal {
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            width: 90%;
            box-shadow: 0 16px 48px rgba(0,0,0,0.5);
        }
        .modal-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text);
        }
        .modal-text {
            font-size: 13px;
            color: var(--text2);
            margin-bottom: 20px;
            line-height: 1.5;
        }
        .modal-buttons {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        .modal-btn {
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid var(--border);
        }
        .modal-btn.cancel {
            background: var(--bg3);
            color: var(--text);
        }
        .modal-btn.cancel:hover { background: var(--bg4); }
        .modal-btn.delete {
            background: var(--danger);
            color: white;
            border-color: var(--danger);
        }
        .modal-btn.delete:hover { opacity: 0.9; }
        
        /* Examples Section */
        .examples { padding: 12px; border-top: 1px solid var(--border); }
        .ex-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text3);
            margin-bottom: 8px;
            font-weight: 600;
        }
        .ex {
            padding: 8px 10px;
            background: var(--bg3);
            border-radius: 6px;
            margin-bottom: 4px;
            font-size: 11px;
            color: var(--text2);
            cursor: pointer;
            transition: all 0.15s ease;
            border: 1px solid transparent;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .ex:hover {
            background: var(--bg4);
            border-color: var(--border);
            color: var(--text);
        }
        .tag {
            font-size: 8px;
            padding: 2px 5px;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        .tag.sama { background: rgba(88, 166, 255, 0.15); color: var(--sama); }
        .tag.cma { background: rgba(63, 185, 80, 0.15); color: var(--cma); }
        .lang-section { margin-top: 10px; }
        .lang-section .ex { direction: rtl; text-align: right; }
        
        /* Status */
        .status {
            padding: 12px 14px;
            border-top: 1px solid var(--border);
            font-size: 10px;
            color: var(--text3);
            background: var(--bg);
        }
        .status-row { display: flex; align-items: center; gap: 8px; }
        .dot {
            width: 6px;
            height: 6px;
            background: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent);
        }
        .dot.loading { animation: pulse 1.5s infinite; }
        @keyframes pulse { 50% { opacity: 0.3; } }
        
        /* Main Area */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
            background: var(--bg);
        }
        .header {
            padding: 10px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg2);
        }
        .header-title { font-size: 12px; color: var(--text2); font-weight: 500; }
        .badge {
            padding: 4px 10px;
            background: var(--bg3);
            border-radius: 12px;
            font-size: 10px;
            color: var(--text3);
            font-weight: 500;
            border: 1px solid var(--border);
        }
        
        /* Chat Area */
        .chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            -webkit-user-select: text;
            user-select: text;
        }
        
        /* Welcome Screen */
        .welcome {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
        }
        .welcome-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px rgba(0, 212, 170, 0.25);
        }
        .welcome-icon svg { width: 32px; height: 32px; fill: var(--bg); }
        .welcome h1 {
            font-size: 26px;
            margin-bottom: 8px;
            background: linear-gradient(90deg, var(--accent), #7c72ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .welcome p { color: var(--text2); max-width: 440px; line-height: 1.6; font-size: 13px; }
        .welcome-stats { display: flex; gap: 10px; margin-top: 24px; }
        .stat {
            background: var(--bg3);
            padding: 12px 18px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid var(--border);
            min-width: 80px;
        }
        .stat-val { font-size: 22px; font-weight: 700; color: var(--accent); }
        .stat-lbl { font-size: 9px; color: var(--text3); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Messages */
        .msg {
            display: flex;
            gap: 12px;
            margin-bottom: 18px;
            max-width: 820px;
            animation: fadeIn 0.25s ease;
        }
        .msg.user {
            flex-direction: row-reverse;
            margin-left: auto;
            margin-right: 0;
        }
        .msg.assistant {
            margin-left: 0;
            margin-right: auto;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        
        .avatar {
            width: 30px;
            height: 30px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 10px;
            flex-shrink: 0;
        }
        .msg.user .avatar { background: var(--bg3); color: var(--text2); border: 1px solid var(--border); }
        .msg.assistant .avatar { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: var(--bg); }
        .msg.assistant .avatar svg { width: 14px; height: 14px; fill: var(--bg); }
        
        .msg-body { flex: 1; min-width: 0; }
        .msg.user .msg-body { text-align: right; }
        
        .msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
        .msg.user .msg-header { justify-content: flex-end; }
        .msg-role { font-size: 11px; font-weight: 600; color: var(--text2); }
        
        .reg { font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
        .reg.sama { background: rgba(88, 166, 255, 0.15); color: var(--sama); }
        .reg.cma { background: rgba(63, 185, 80, 0.15); color: var(--cma); }
        .reg.both { background: rgba(168, 85, 247, 0.15); color: #a371f7; }
        
        .msg-text {
            line-height: 1.65;
            font-size: 14px;
            color: var(--text);
            -webkit-user-select: text;
            user-select: text;
        }
        .msg.user .msg-text {
            background: var(--bg3);
            padding: 10px 14px;
            border-radius: 12px 12px 4px 12px;
            display: inline-block;
            border: 1px solid var(--border);
        }
        .msg-text.rtl { direction: rtl; text-align: right; }
        .msg-text p { margin-bottom: 10px; }
        .msg-text p:last-child { margin-bottom: 0; }
        .msg-text ul, .msg-text ol { margin: 10px 0; padding-left: 20px; }
        .msg-text.rtl ul, .msg-text.rtl ol { padding-left: 0; padding-right: 20px; }
        .msg-text li { margin-bottom: 5px; }
        .msg-text strong { color: var(--accent); font-weight: 600; }
        .msg-text code { background: var(--bg3); padding: 2px 5px; border-radius: 4px; font-size: 13px; }
        .msg-text h1, .msg-text h2, .msg-text h3 { margin: 14px 0 6px; color: var(--text); font-size: 15px; }
        
        /* Sources */
        .sources { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); }
        .src-title { font-size: 9px; text-transform: uppercase; letter-spacing: 1px; color: var(--text3); margin-bottom: 6px; font-weight: 600; }
        .src {
            display: inline-block;
            background: var(--bg3);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 10px;
            color: var(--text2);
            margin-right: 4px;
            margin-bottom: 4px;
            border: 1px solid var(--border);
        }
        
        /* Loading */
        .loading-msg { display: flex; align-items: center; gap: 10px; color: var(--text3); font-size: 13px; }
        .dots { display: flex; gap: 3px; }
        .dots span { width: 5px; height: 5px; background: var(--accent); border-radius: 50%; animation: bounce 1.4s infinite; }
        .dots span:nth-child(2) { animation-delay: 0.2s; }
        .dots span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; } 40% { transform: scale(1); opacity: 1; } }
        
        /* Input Area */
        .input-area {
            padding: 14px 20px 18px;
            border-top: 1px solid var(--border);
            background: var(--bg2);
        }
        .input-box {
            max-width: 820px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
            background: var(--bg3);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 10px 14px;
            transition: all 0.2s ease;
        }
        .input-box:focus-within {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.08);
        }
        .input-box textarea {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text);
            font-family: inherit;
            font-size: 14px;
            resize: none;
            outline: none;
            max-height: 120px;
            line-height: 1.5;
            padding: 4px 0;
        }
        .input-box textarea::placeholder { color: var(--text3); }
        .send {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border: none;
            border-radius: 8px;
            width: 36px;
            height: 36px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            align-self: flex-end;
            transition: all 0.15s ease;
        }
        .send:hover { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3); }
        .send:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }
        .send svg { width: 16px; height: 16px; fill: var(--bg); }
        
        /* Overlay */
        .overlay {
            position: fixed;
            inset: 0;
            background: rgba(10, 13, 16, 0.98);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 16px;
            z-index: 100;
        }
        .overlay.hidden { display: none; }
        .spinner {
            width: 40px;
            height: 40px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .overlay-text { color: var(--text2); font-size: 13px; }
    </style>
</head>
<body>
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <div class="logo-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" fill="none"/>
                    </svg>
                </div>
                <div>
                    <div class="logo-text">TadqeeqAI</div>
                    <div class="logo-sub">SAMA · CMA · EN/AR</div>
                </div>
            </div>
            <button class="new-chat-btn" id="newChatBtn">
                <svg viewBox="0 0 24 24" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                New Chat
            </button>
        </div>
        <div class="chat-history" id="chatHistory">
            <div class="history-title">Recent Chats</div>
        </div>
        <div class="examples">
            <div class="ex-title">Try These</div>
            <div class="ex" data-q="What are the licensing fees for finance companies?"><span>Licensing fees</span><span class="tag sama">SAMA</span></div>
            <div class="ex" data-q="What is a qualified investor?"><span>Qualified investor</span><span class="tag cma">CMA</span></div>
            <div class="lang-section">
                <div class="ex" data-q="ما هي رسوم ترخيص شركات التمويل؟"><span class="tag sama">SAMA</span><span>رسوم الترخيص</span></div>
                <div class="ex" data-q="ما هو المستثمر المؤهل؟"><span class="tag cma">CMA</span><span>المستثمر المؤهل</span></div>
            </div>
        </div>
        <div class="status">
            <div class="status-row"><div class="dot loading" id="dot"></div><span id="status">Initializing...</span></div>
        </div>
    </aside>
    <main class="main">
        <header class="header">
            <span class="header-title">Saudi Financial Regulations Assistant</span>
            <div class="badge">Hybrid Search · Aya 8B</div>
        </header>
        <div class="chat" id="chat">
            <div class="welcome" id="welcome">
                <div class="welcome-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" fill="none"/>
                    </svg>
                </div>
                <h1>TadqeeqAI</h1>
                <p>Bilingual AI assistant for Saudi Arabian financial regulations. Query SAMA and CMA documents in English or Arabic with accurate, cited responses.</p>
                <div class="welcome-stats">
                    <div class="stat"><div class="stat-val" id="s-sama">-</div><div class="stat-lbl">SAMA</div></div>
                    <div class="stat"><div class="stat-val" id="s-cma">-</div><div class="stat-lbl">CMA</div></div>
                    <div class="stat"><div class="stat-val" id="s-total">-</div><div class="stat-lbl">Articles</div></div>
                </div>
            </div>
        </div>
        <div class="input-area">
            <div class="input-box">
                <textarea id="input" placeholder="Ask about SAMA or CMA regulations..." rows="1" disabled></textarea>
                <button class="send" id="send" disabled><svg viewBox="0 0 24 24"><path d="M2 21L23 12 2 3 2 10 17 12 2 14z"/></svg></button>
            </div>
        </div>
    </main>
    <div class="overlay" id="overlay"><div class="spinner"></div><div class="overlay-text">Loading TadqeeqAI...</div></div>
    
    <!-- Delete Confirmation Modal -->
    <div class="modal-overlay" id="deleteModal">
        <div class="modal">
            <div class="modal-title">Delete Chat</div>
            <div class="modal-text">Are you sure you want to delete this chat? This action is permanent and cannot be undone.</div>
            <div class="modal-buttons">
                <button class="modal-btn cancel" id="cancelDelete">Cancel</button>
                <button class="modal-btn delete" id="confirmDelete">Delete</button>
            </div>
        </div>
    </div>
    
    <script>
        const chat=document.getElementById('chat'),input=document.getElementById('input'),sendBtn=document.getElementById('send'),dot=document.getElementById('dot'),statusEl=document.getElementById('status');
        const chatHistoryEl=document.getElementById('chatHistory');
        const deleteModal=document.getElementById('deleteModal');
        let ready=false,busy=false,currentChatId=null,chatToDelete=null;
        
        marked.setOptions({breaks:true,gfm:true});
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if(!e.target.closest('.history-item-menu') && !e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.show').forEach(d => d.classList.remove('show'));
            }
        });
        
        // Modal handlers
        document.getElementById('cancelDelete').addEventListener('click', () => {
            deleteModal.classList.remove('show');
            chatToDelete = null;
        });
        
        document.getElementById('confirmDelete').addEventListener('click', async () => {
            if(chatToDelete) {
                await deleteChat(chatToDelete);
                deleteModal.classList.remove('show');
                chatToDelete = null;
            }
        });
        
        async function deleteChat(chatId) {
            try {
                const r = await window.pywebview.api.delete_chat(chatId);
                if(r.success) {
                    renderChatHistory(r.chats);
                    if(chatId === currentChatId) {
                        await newChat(true);
                    }
                }
            } catch(e) {
                console.error('deleteChat error:', e);
            }
        }
        
        function showDeleteConfirm(chatId) {
            chatToDelete = chatId;
            deleteModal.classList.add('show');
        }
        
        async function init(){
            try{
                const r=await window.pywebview.api.initialize();
                if(r.status==='ready'){
                    ready=true;
                    dot.classList.remove('loading');
                    statusEl.textContent=r.total+' articles indexed';
                    document.getElementById('s-sama').textContent=r.sama;
                    document.getElementById('s-cma').textContent=r.cma;
                    document.getElementById('s-total').textContent=r.total;
                    input.disabled=false;
                    sendBtn.disabled=false;
                    document.getElementById('overlay').classList.add('hidden');
                    input.focus();
                    // Load chat history
                    if(r.chats) renderChatHistory(r.chats);
                    // Start new chat
                    await newChat(false);
                }else{
                    statusEl.textContent='Error: '+r.message;
                }
            }catch(e){
                statusEl.textContent='Error: '+e.message;
            }
        }
        window.addEventListener('pywebviewready',init);
        
        function renderChatHistory(chats){
            let html='<div class="history-title">Recent Chats</div>';
            chats.forEach(c=>{
                const isActive=c.id===currentChatId?' active':'';
                html+=`<div class="history-item${isActive}" data-id="${c.id}">
                    <span class="history-item-text">${escHtml(c.preview)}</span>
                    <div class="history-item-menu" data-id="${c.id}">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="6" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="18" r="1.5"/></svg>
                    </div>
                    <div class="dropdown" data-id="${c.id}">
                        <div class="dropdown-item delete-chat" data-id="${c.id}">
                            <svg viewBox="0 0 24 24" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14"/></svg>
                            Delete
                        </div>
                    </div>
                </div>`;
            });
            chatHistoryEl.innerHTML=html;
            
            // Add click handlers for chat items
            chatHistoryEl.querySelectorAll('.history-item').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    if(!e.target.closest('.history-item-menu') && !e.target.closest('.dropdown')) {
                        loadChat(el.dataset.id);
                    }
                });
            });
            
            // Add click handlers for menu buttons
            chatHistoryEl.querySelectorAll('.history-item-menu').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    e.stopPropagation();
                    const dropdown = el.nextElementSibling;
                    document.querySelectorAll('.dropdown.show').forEach(d => {
                        if(d !== dropdown) d.classList.remove('show');
                    });
                    dropdown.classList.toggle('show');
                });
            });
            
            // Add click handlers for delete buttons
            chatHistoryEl.querySelectorAll('.delete-chat').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    e.stopPropagation();
                    showDeleteConfirm(el.dataset.id);
                });
            });
        }
        
        async function newChat(updateUI=true){
            try{
                const r=await window.pywebview.api.new_chat();
                currentChatId=r.id;
                if(updateUI){
                    // Clear chat
                    chat.innerHTML='<div class="welcome" id="welcome"><div class="welcome-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" fill="none"/></svg></div><h1>TadqeeqAI</h1><p>Bilingual AI assistant for Saudi Arabian financial regulations.</p></div>';
                    renderChatHistory(r.chats);
                }
            }catch(e){
                console.error('newChat error:',e);
            }
        }
        
        async function loadChat(chatId){
            try{
                const r=await window.pywebview.api.load_chat(chatId);
                currentChatId=chatId;
                // Clear and render messages
                chat.innerHTML='';
                r.messages.forEach(m=>{
                    addMsg(m.role,m.content,m.sources||null,m.regulator||null);
                });
                // Update active state
                chatHistoryEl.querySelectorAll('.history-item').forEach(el=>{
                    el.classList.toggle('active',el.dataset.id===chatId);
                });
            }catch(e){
                console.error('loadChat error:',e);
            }
        }
        
        document.getElementById('newChatBtn').addEventListener('click',()=>newChat(true));
        
        input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,120)+'px';});
        input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
        sendBtn.addEventListener('click',send);
        document.querySelectorAll('.ex').forEach(el=>{el.addEventListener('click',()=>{input.value=el.dataset.q;send();});});
        
        function escHtml(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML;}
        function renderMd(text){try{return marked.parse(text);}catch(e){return escHtml(text);}}
        function isArabic(text){return /[\u0600-\u06FF]/.test(text)&&(text.match(/[\u0600-\u06FF]/g)||[]).length>text.length*0.3;}
        
        const logoSvg='<svg viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" fill="none"/></svg>';
        
        function addMsg(role,text,sources,reg){
            const w=document.getElementById('welcome');if(w)w.style.display='none';
            const div=document.createElement('div');
            div.className='msg '+role;
            let regHtml=reg&&reg!=='NONE'?'<span class="reg '+reg.toLowerCase()+'">'+reg+'</span>':'';
            let srcHtml='';
            if(sources&&sources.length){
                srcHtml='<div class="sources"><div class="src-title">Sources</div>';
                sources.forEach(s=>{srcHtml+='<span class="src">'+escHtml(s.article)+'</span>';});
                srcHtml+='</div>';
            }
            const textHtml=role==='assistant'?renderMd(text):escHtml(text);
            const rtlClass=isArabic(text)?' rtl':'';
            const avatarContent=role==='user'?'You':logoSvg;
            div.innerHTML='<div class="avatar">'+avatarContent+'</div><div class="msg-body"><div class="msg-header"><span class="msg-role">'+(role==='user'?'You':'TadqeeqAI')+'</span>'+regHtml+'</div><div class="msg-text'+rtlClass+'">'+textHtml+'</div>'+srcHtml+'</div>';
            chat.appendChild(div);
            chat.scrollTop=chat.scrollHeight;
        }
        
        function addLoading(){
            const w=document.getElementById('welcome');if(w)w.style.display='none';
            const div=document.createElement('div');
            div.className='msg assistant';
            div.id='loading';
            div.innerHTML='<div class="avatar">'+logoSvg+'</div><div class="msg-body"><div class="msg-header"><span class="msg-role">TadqeeqAI</span></div><div class="loading-msg"><div class="dots"><span></span><span></span><span></span></div><span>Searching regulations...</span></div></div>';
            chat.appendChild(div);
            chat.scrollTop=chat.scrollHeight;
        }
        
        async function send(){
            const q=input.value.trim();
            if(!q||busy||!ready)return;
            busy=true;
            sendBtn.disabled=true;
            input.disabled=true;
            input.value='';
            input.style.height='auto';
            addMsg('user',q,null,null);
            addLoading();
            try{
                const r=await window.pywebview.api.query(q);
                document.getElementById('loading')?.remove();
                addMsg('assistant',r.answer,r.sources,r.regulator);
                // Refresh chat history
                const chats=await window.pywebview.api.get_chats();
                renderChatHistory(chats.chats);
            }catch(e){
                document.getElementById('loading')?.remove();
                addMsg('assistant','An error occurred while processing your request.',null,null);
            }
            busy=false;
            sendBtn.disabled=false;
            input.disabled=false;
            input.focus();
        }
    </script>
</body>
</html>'''

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   TADQEEQAI v2.1")
    print("   Hybrid Search: BM25 + Semantic")
    print("   SAMA + CMA · English + Arabic")
    print("   Chat History · Follow-up Support")
    print("="*50 + "\n")
    api = API()
    window = webview.create_window('TadqeeqAI v2.1', html=HTML, js_api=api, width=1200, height=800, min_size=(900,600), background_color='#0f1419', text_select=True)
    webview.start(debug=False)
