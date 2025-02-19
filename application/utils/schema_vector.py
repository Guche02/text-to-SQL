import chromadb
from sentence_transformers import SentenceTransformer
import spacy

nlp = spacy.load("en_core_web_sm")

def split_text_by_sentence(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

with open("D:\\Internship\\text-to-SQL\\application\\utils\\schema.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = split_text_by_sentence(text)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = embedding_model.encode(chunks).tolist()

chroma_client = chromadb.PersistentClient(path="D:\\Internship\\text-to-SQL\\application\\chroma")
collection = chroma_client.get_or_create_collection(name="sql_data")

for i, chunk in enumerate(chunks):
    collection.add(
        ids=[str(i)],  
        documents=[chunk],  
        embeddings=[embeddings[i]]  
    )

print("Text has been successfully processed and stored in ChromaDB.")
collection