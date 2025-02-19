import chromadb
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="D:\\Internship\\text-to-SQL\\application\\chroma")
collection = chroma_client.get_collection(name="sql_data")

def retrieve_schema(query: str, top_n: int = 10):
    """
    Queries the ChromaDB vector store using semantic similarity search.

    Args:
        query (str): The input query.
        top_n (int, optional): The number of top similar results to return. Defaults to 5.

    Returns:
        list: A list of retrieved documents with similarity scores.
    """
    query_embedding = embedding_model.encode(query).tolist()  
    results = collection.query(
        query_embeddings=[query_embedding], 
        n_results=top_n
    )

    retrieved_docs = []
    for  doc in enumerate(results["documents"][0]):
        retrieved_docs.append((doc))

    return retrieved_docs

# query = "In which store was customer with email 'MARY.SMITH@sakilacustomer.org' registered in?"
# results = retrieve_schema(query)

# print("results: ", results)

# print("\nTop Retrieved Results:")
# for i, (doc) in enumerate(results):
#     print(f"Result {i+1} (\n{doc}\n")

