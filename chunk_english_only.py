import json
import re
from pathlib import Path


def chunk_document(full_text, source_name, min_length=50):
    """Split a legal document into article-based chunks."""
    
    patterns = [
        (r'(Article \d+)', 'standard'),
        (r'(Article \([0-9]+\))', 'parens'),
    ]
    
    best_pattern = None
    best_type = None
    best_count = 0
    
    for pattern, ptype in patterns:
        matches = re.findall(pattern, full_text)
        if len(matches) > best_count:
            best_count = len(matches)
            best_pattern = pattern
            best_type = ptype
    
    if best_count < 3:
        print(f"  Warning: No article pattern found, skipping")
        return []
    
    print(f"  Pattern: {best_type} ({best_count} articles)")
    
    parts = re.split(best_pattern, full_text)
    articles = []
    
    intro = parts[0].strip()
    if intro and len(intro) >= min_length:
        articles.append({
            "source": source_name,
            "chunk_id": "Introduction",
            "text": intro[:3000]
        })
    
    for i in range(1, len(parts) - 1, 2):
        label = parts[i].strip()
        content = parts[i + 1].strip()
        
        num_match = re.search(r'\d+', label)
        article_num = num_match.group() if num_match else str(i//2)
        
        full_text_chunk = f"{label}: {content}"
        
        articles.append({
            "source": source_name,
            "chunk_id": f"Article {article_num}",
            "text": full_text_chunk
        })
    
    seen = set()
    unique = []
    for art in articles:
        if art['chunk_id'] not in seen:
            seen.add(art['chunk_id'])
            if len(art['text']) >= min_length:
                unique.append(art)
    
    return unique


def main():
    input_file = Path('clean_knowledge_base_v2.json')
    output_file = Path('knowledge_base_english.json')
    
    print("=" * 50)
    print("ShariaGuide - English Document Chunker")
    print("=" * 50)
    
    print(f"\nLoading: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        page_data = json.load(f)
    
    english_docs = {}
    for chunk in page_data:
        src = chunk['source']
        if 'Arabic' in src or 'arabic' in src:
            continue
        if src not in english_docs:
            english_docs[src] = []
        english_docs[src].append(chunk)
    
    print(f"Found {len(english_docs)} English documents\n")
    
    all_chunks = []
    
    for source_name, pages in english_docs.items():
        print(f"Processing: {source_name}")
        
        pages.sort(key=lambda x: x['page_number'])
        full_text = "\n\n".join([p['text'] for p in pages])
        
        chunks = chunk_document(full_text, source_name, min_length=50)
        all_chunks.extend(chunks)
        
        print(f"  -> {len(chunks)} chunks\n")
    
    print(f"Saving to: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    
    print(f"\nDONE!")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"File size: {output_file.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
