from sentence_transformers import SentenceTransformer
from langchain.tools import tool
import chromadb

client = chromadb.PersistentClient(path="D:\\Internship\\text-to-SQL\\application\\chroma")
collection = client.get_collection("sql_data")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_schema(query: str, top_n: int = 5) -> str:
    """
    Retrieves the top N schema documents from a vector database based on the query.

    Args:
        query (str): The input query for which schema-related documents are to be retrieved.
        top_n (int, optional): The number of top documents to return. Defaults to 3.

    Returns:
        str: A formatted string containing the top N retrieved schema documents, including table names and corresponding information.
    """
    query_embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_n
    )

    retrieved_docs = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        retrieved_docs.append(f"Table: {meta['name']}\nInfo: {doc}\n")

    return "\n".join(retrieved_docs)

# response = retrieve_schema("how many films are there in the inventory?")
# print(response)