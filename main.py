"""
TadqeeqAI v2.0
==============
Bilingual RAG system for Saudi Arabian financial regulations.
SAMA + CMA · English + Arabic

Key Features:
- Hybrid Search: BM25 (keyword) + Semantic (embeddings)
- Article-level chunking with full context
- Single multilingual embedding model (E5-base)

Prerequisites:
    1. Run build_embeddings.py first
    2. Ensure Ollama is running with aya:8b model
"""

import json
import pickle
import re
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
EMBEDDING_MODEL = 'intfloat/multilingual-e5-base'

# LLM Model Options:
# - 'aya:8b'       : Best for Arabic, no Chinese leak, follows instructions well
# - 'qwen2.5:7b'   : Good overall but leaks Chinese on long Arabic responses  
# - 'jais:13b'     : Arabic-first but truncates responses
LLM_MODEL = 'aya:8b'


class TadqeeqRAG:
    """Hybrid RAG system with BM25 + semantic search."""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        print("Loading TadqeeqAI v2.0...")
        
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
        
        print("\n✓ TadqeeqAI v2.0 Ready!\n")
    
    def _warmup_llm(self):
        try:
            ollama.generate(model=LLM_MODEL, prompt="test", options={"num_predict": 1})
        except:
            print(f"      Pulling {LLM_MODEL}...")
            ollama.pull(LLM_MODEL)
    
    def detect_language(self, text):
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        return 'ar' if arabic_chars > len(text) * 0.3 else 'en'
    
    def detect_regulator(self, question):
        q = question.lower()
        # Also check original for Arabic (case doesn't apply)
        q_orig = question
        
        sama_kw = ['finance company', 'finance companies', 'license fee', 'licensing fee', 'microfinance',
                   'real estate finance', 'mortgage', 'borrower', 'lending', 'sama', 'monetary']
        sama_ar = ['شركة تمويل', 'شركات التمويل', 'رسوم الترخيص', 'رسوم ترخيص', 'تمويل عقاري',
                   'مؤسسة النقد', 'ساما', 'مقابل مالي', 'المقابل المالي', 'شركات تمويل']
        
        cma_kw = ['securities', 'capital market', 'investment fund', 'sukuk', 'qualified investor',
                  'prospectus', 'listing', 'ipo', 'merger', 'acquisition', 'debt instrument', 'cma']
        cma_ar = ['أوراق مالية', 'سوق المال', 'صندوق استثمار', 'صكوك', 'مستثمر مؤهل', 'المستثمر المؤهل',
                  'هيئة السوق المالية', 'هيئة السوق', 'اندماج', 'استحواذ', 'أدوات دين', 'طرح',
                  'صناديق الاستثمار', 'الصكوك', 'طرح عام', 'طرح خاص', 'نشرة الإصدار']
        
        sama_score = sum(1 for kw in sama_kw if kw in q) + sum(1 for kw in sama_ar if kw in q_orig)
        cma_score = sum(1 for kw in cma_kw if kw in q) + sum(1 for kw in cma_ar if kw in q_orig)
        
        if sama_score > 0 and cma_score == 0: return 'SAMA'
        elif cma_score > 0 and sama_score == 0: return 'CMA'
        elif sama_score > cma_score: return 'SAMA'
        elif cma_score > sama_score: return 'CMA'
        return 'BOTH'
    
    def translate_arabic_query(self, query):
        """Translate Arabic query to English for cross-lingual search."""
        # Direct term mappings (Arabic → English)
        ar_to_en = {
            # Licensing & Fees
            'رسوم ترخيص': 'licensing fees license fee',
            'رسوم الترخيص': 'licensing fees license fee', 
            'مقابل مالي': 'licensing fees financial consideration fee',
            'المقابل المالي': 'licensing fees financial consideration fee',
            'رسوم': 'fees',
            'ترخيص': 'license licensing',
            # Companies & Entities
            'شركات التمويل': 'finance companies',
            'شركة تمويل': 'finance company',
            'شركة': 'company',
            'شركات': 'companies',
            # Investment
            'مستثمر مؤهل': 'qualified investor',
            'المستثمر المؤهل': 'qualified investor',
            'صندوق استثمار': 'investment fund',
            'صناديق الاستثمار': 'investment funds',
            'صناديق': 'funds',
            # Securities & Sukuk - CRITICAL
            'صكوك': 'sukuk debt instruments securities',
            'الصكوك': 'sukuk debt instruments securities',
            'أدوات دين': 'debt instruments sukuk securities',
            'أوراق مالية': 'securities',
            'طرح': 'offering offer issuance',
            'إصدار': 'issuance issue offering',
            'اكتتاب': 'subscription IPO offering',
            'طرح عام': 'public offering IPO',
            'طرح خاص': 'private placement',
            # Capital & Requirements
            'رأس المال': 'capital',
            'متطلبات رأس المال': 'capital requirements minimum capital',
            'الحد الأدنى': 'minimum',
            'متطلبات': 'requirements',
            # Real Estate
            'تمويل عقاري': 'real estate finance mortgage',
            'عقاري': 'real estate',
            # Regulators
            'ساما': 'SAMA central bank',
            'مؤسسة النقد': 'SAMA central bank monetary authority',
            'هيئة السوق المالية': 'CMA capital market authority',
            'هيئة السوق': 'CMA capital market',
            # M&A
            'اندماج': 'merger',
            'استحواذ': 'acquisition',
            'الاندماج والاستحواذ': 'merger acquisition',
            # General
            'ما هي': 'what are',
            'ما هو': 'what is',
            'كيف': 'how',
            'شروط': 'conditions requirements',
            'نظام': 'law regulation system',
            'لائحة': 'regulation implementing',
            # Microfinance
            'تمويل متناهي الصغر': 'microfinance',
            'متناهي الصغر': 'microfinance',
        }
        
        english_terms = []
        
        for ar_term, en_term in ar_to_en.items():
            if ar_term in query:
                english_terms.append(en_term)
        
        if english_terms:
            return ' '.join(english_terms)
        
        # Fallback: return original (will use semantic similarity)
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
        """BM25 keyword search. If force_english, search English docs regardless of query language."""
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
        """Semantic search. If force_english, search English docs regardless of query language."""
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
        """
        Hybrid search with English Bridge strategy.
        For Arabic queries: translate to English, search English docs, respond in Arabic.
        """
        user_language = self.detect_language(query)
        regulator = self.detect_regulator(query)
        
        # ENGLISH BRIDGE: For Arabic queries, translate and search English docs
        if user_language == 'ar':
            english_query = self.translate_arabic_query(query)
            expanded = self.expand_query(english_query, 'en')
            print(f"DEBUG: Arabic Query → English Bridge")
            print(f"  Original: {query[:50]}")
            print(f"  Translated: {english_query[:50]}")
            print(f"  Regulator: {regulator}")
            
            # Search ENGLISH documents with translated query
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
    
    def build_prompt(self, question, docs, language):
        """
        Build LLM prompt optimized for Aya model.
        """
        ctx = "\n\n---\n\n".join([f"[Document {i}]\nSource: {d['document']}\nArticle: {d['article']}\nContent:\n{d['text']}" 
                                  for i, d in enumerate(docs, 1)])
        
        if language == 'ar':
            # Arabic prompt for Aya
            return f"""أنت مساعد قانوني متخصص في الأنظمة المالية السعودية.

مهمتك: اقرأ المستندات بعناية وأجب على السؤال باللغة العربية.

تعليمات مهمة:
- اقرأ كل مستند بعناية قبل الإجابة
- استخرج المعلومات المطلوبة من المستندات
- اذكر رقم المادة عند الاستشهاد (مثال: المادة 22)
- مصطلح "debt instruments" يعني "الصكوك" أو "أدوات الدين"
- اكتب الأرقام والمبالغ كما هي في المستند
- استخدم تنسيق Markdown: استخدم **نص** للتأكيد و - للقوائم
- إذا لم تجد المعلومة المحددة، قل ذلك بوضوح

المستندات المرجعية:
{ctx}

السؤال: {question}

الإجابة:"""
        
        # English prompt for Aya
        return f"""You are a legal assistant specializing in Saudi Arabian financial regulations.

Your task: Carefully read the documents below and answer the question.

Important instructions:
- Read each document carefully before answering
- Extract the relevant information from the documents
- Cite the Article number when referencing information
- "Sukuk" and "debt instruments" refer to the same thing
- Preserve exact numbers and amounts as written in the documents
- If the specific information is not found, say so clearly

Reference Documents:
{ctx}

Question: {question}

Answer:"""
    
    def generate_response(self, question):
        docs, reg, lang = self.hybrid_search(question)
        if not docs:
            return {'answer': 'No relevant information found.' if lang == 'en' else 'لم يتم العثور على معلومات ذات صلة.', 'sources': [], 'regulator': reg}
        prompt = self.build_prompt(question, docs, lang)
        resp = ollama.generate(model=LLM_MODEL, prompt=prompt, options={'temperature': 0.1, 'num_predict': 2000})
        seen = set()
        sources = [{'article': d['article'], 'document': d['document']} for d in docs if d['article'] not in seen and not seen.add(d['article'])]
        return {'answer': resp['response'].strip(), 'sources': sources, 'regulator': reg}


class API:
    def initialize(self):
        try:
            print("API.initialize() called...")
            rag = TadqeeqRAG.get_instance()
            print("RAG instance created successfully")
            return {'status': 'ready', 'total': rag.total, 'sama': rag.sama_count, 'cma': rag.cma_count,
                    'sama_en': rag.stats['SAMA']['en'], 'sama_ar': rag.stats['SAMA']['ar'],
                    'cma_en': rag.stats['CMA']['en'], 'cma_ar': rag.stats['CMA']['ar']}
        except Exception as e:
            print(f"API.initialize() ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'error', 'message': str(e)}
    
    def query(self, question):
        return TadqeeqRAG.get_instance().generate_response(question)


HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TadqeeqAI v2.0</title>
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
        
        /* Custom Scrollbar - macOS style */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--text3); }
        
        /* Selection */
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
            padding: 20px;
            border-bottom: 1px solid var(--border);
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-icon {
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .logo-icon svg {
            width: 24px;
            height: 24px;
            fill: var(--bg);
        }
        .logo-text { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; }
        .logo-sub { font-size: 10px; color: var(--text3); margin-top: 2px; letter-spacing: 0.5px; }
        
        /* Examples */
        .examples { padding: 16px; flex: 1; overflow-y: auto; }
        .ex-title {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text3);
            margin-bottom: 10px;
            font-weight: 600;
        }
        .ex {
            padding: 10px 12px;
            background: var(--bg3);
            border-radius: 8px;
            margin-bottom: 6px;
            font-size: 12px;
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
            font-size: 9px;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 600;
            text-transform: uppercase;
            flex-shrink: 0;
        }
        .tag.sama { background: rgba(88, 166, 255, 0.15); color: var(--sama); }
        .tag.cma { background: rgba(63, 185, 80, 0.15); color: var(--cma); }
        .lang-section {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
        }
        .lang-section .ex { direction: rtl; text-align: right; }
        .lang-section .tag { margin-left: 0; margin-right: auto; }
        
        /* Status */
        .status {
            padding: 14px 16px;
            border-top: 1px solid var(--border);
            font-size: 11px;
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
        .status-details {
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid var(--border);
            font-size: 10px;
            line-height: 1.6;
            color: var(--text3);
        }
        
        /* Main Area */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            min-width: 0;
            background: var(--bg);
        }
        .header {
            padding: 12px 24px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg2);
        }
        .header-title { font-size: 13px; color: var(--text2); font-weight: 500; }
        .badge {
            padding: 5px 12px;
            background: var(--bg3);
            border-radius: 16px;
            font-size: 10px;
            color: var(--text3);
            font-weight: 500;
            border: 1px solid var(--border);
        }
        
        /* Chat Area */
        .chat {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
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
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 212, 170, 0.25);
        }
        .welcome-icon svg { width: 36px; height: 36px; fill: var(--bg); }
        .welcome h1 {
            font-size: 28px;
            margin-bottom: 10px;
            background: linear-gradient(90deg, var(--accent), #7c72ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        .welcome p { color: var(--text2); max-width: 460px; line-height: 1.6; font-size: 13px; }
        .welcome-stats { display: flex; gap: 12px; margin-top: 28px; }
        .stat {
            background: var(--bg3);
            padding: 14px 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid var(--border);
            min-width: 90px;
        }
        .stat-val { font-size: 24px; font-weight: 700; color: var(--accent); }
        .stat-lbl { font-size: 9px; color: var(--text3); margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Messages */
        .msg {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            max-width: 850px;
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
            width: 32px;
            height: 32px;
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
        .msg.assistant .avatar svg { width: 16px; height: 16px; fill: var(--bg); }
        
        .msg-body { flex: 1; min-width: 0; }
        .msg.user .msg-body { text-align: right; }
        
        .msg-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
        .msg.user .msg-header { justify-content: flex-end; }
        .msg-role { font-size: 12px; font-weight: 600; color: var(--text2); }
        
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
            padding: 16px 24px 20px;
            border-top: 1px solid var(--border);
            background: var(--bg2);
        }
        .input-box {
            max-width: 850px;
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
        </div>
        <div class="examples">
            <div class="ex-title">English Examples</div>
            <div class="ex" data-q="What are the licensing fees for finance companies?"><span>Licensing fees</span><span class="tag sama">SAMA</span></div>
            <div class="ex" data-q="What is a qualified investor?"><span>Qualified investor</span><span class="tag cma">CMA</span></div>
            <div class="ex" data-q="What are the requirements for sukuk issuance?"><span>Sukuk issuance</span><span class="tag cma">CMA</span></div>
            <div class="ex" data-q="What are the capital requirements for finance companies?"><span>Capital requirements</span><span class="tag sama">SAMA</span></div>
            <div class="lang-section">
                <div class="ex-title">أمثلة عربية</div>
                <div class="ex" data-q="ما هي رسوم ترخيص شركات التمويل؟"><span class="tag sama">SAMA</span><span>رسوم الترخيص</span></div>
                <div class="ex" data-q="ما هو المستثمر المؤهل؟"><span class="tag cma">CMA</span><span>المستثمر المؤهل</span></div>
                <div class="ex" data-q="ما هي متطلبات إصدار الصكوك؟"><span class="tag cma">CMA</span><span>متطلبات الصكوك</span></div>
                <div class="ex" data-q="ما هي متطلبات رأس المال لشركات التمويل؟"><span class="tag sama">SAMA</span><span>متطلبات رأس المال</span></div>
            </div>
        </div>
        <div class="status">
            <div class="status-row"><div class="dot loading" id="dot"></div><span id="status">Initializing...</span></div>
            <div class="status-details" id="details"></div>
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
    <script>
        const chat=document.getElementById('chat'),input=document.getElementById('input'),sendBtn=document.getElementById('send'),dot=document.getElementById('dot'),statusEl=document.getElementById('status');
        let ready=false,busy=false;
        
        marked.setOptions({breaks:true,gfm:true});
        
        async function init(){
            try{
                const r=await window.pywebview.api.initialize();
                if(r.status==='ready'){
                    ready=true;
                    dot.classList.remove('loading');
                    statusEl.textContent=r.total+' articles indexed';
                    document.getElementById('details').innerHTML='SAMA: '+r.sama+' ('+r.sama_en+' EN, '+r.sama_ar+' AR)<br>CMA: '+r.cma+' ('+r.cma_en+' EN, '+r.cma_ar+' AR)';
                    document.getElementById('s-sama').textContent=r.sama;
                    document.getElementById('s-cma').textContent=r.cma;
                    document.getElementById('s-total').textContent=r.total;
                    input.disabled=false;
                    sendBtn.disabled=false;
                    document.getElementById('overlay').classList.add('hidden');
                    input.focus();
                }else{
                    statusEl.textContent='Error: '+r.message;
                }
            }catch(e){
                statusEl.textContent='Error: '+e.message;
            }
        }
        window.addEventListener('pywebviewready',init);
        
        input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,120)+'px';});
        input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
        sendBtn.addEventListener('click',send);
        document.querySelectorAll('.ex').forEach(el=>{el.addEventListener('click',()=>{input.value=el.dataset.q;send();});});
        
        function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML;}
        function renderMd(text){try{return marked.parse(text);}catch(e){return esc(text);}}
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
                sources.forEach(s=>{srcHtml+='<span class="src">'+esc(s.article)+'</span>';});
                srcHtml+='</div>';
            }
            const textHtml=role==='assistant'?renderMd(text):esc(text);
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
    print("   TADQEEQAI v2.0")
    print("   Hybrid Search: BM25 + Semantic")
    print("   SAMA + CMA · English + Arabic")
    print("="*50 + "\n")
    api = API()
    window = webview.create_window('TadqeeqAI v2.0', html=HTML, js_api=api, width=1200, height=800, min_size=(900,600), background_color='#0f1419', text_select=True)
    webview.start(debug=False)
