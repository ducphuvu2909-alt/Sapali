import re
def clean_text(t): t=t.replace('\r','').replace('\t',' '); t=re.sub('\n{3,}','\n\n',t); return t.strip()
def chunk_text(text, chunk_size=1200, overlap=200):
    text=clean_text(text); words=text.split(); chunks=[]; i=0
    while i<len(words): chunks.append(' '.join(words[i:i+chunk_size])); i+= (chunk_size-overlap)
    return chunks
