import os
from pyprojroot import here
import pandas as pd
import chromadb
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
import warnings
warnings.filterwarnings("ignore")

# Global variables
ollama_embeddings = None
ollama_llm = None
vectordb = None

def initialize_data():
    global ollama_embeddings, ollama_llm, vectordb

    # Initialize Ollama for embeddings and text generation
    ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
    ollama_llm = Ollama(model="run deepseek-r1:1.5b")

    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=str(here("data/chroma")))
    collection = chroma_client.get_or_create_collection(name="titanic_small")

    # Read CSV file
    file_dir = here("dealers.csv")
    df = pd.read_csv(file_dir, nrows=5)

    # Prepare data for embedding
    docs = []
    metadatas = []
    ids = []
    embeddings = []

    for index, row in df.iterrows():
        output_str = ""
        for col in df.columns:
            output_str += f"{col}: {row[col]},\n"
        
        # Generate embeddings using Ollama
        embedding = ollama_embeddings.embed_query(output_str)
        
        embeddings.append(embedding)
        docs.append(output_str)
        metadatas.append({"source": "titanic_small"})
        ids.append(f"id{index}")

    # Add documents to the collection
    collection.add(
        documents=docs,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=ids
    )

    # Set the global vectordb
    vectordb = chroma_client.get_collection(name="titanic_small")

def process_and_query(query_texts):
    global ollama_embeddings, ollama_llm, vectordb

    # Generate query embeddings
    query_embeddings = ollama_embeddings.embed_query(query_texts)

    # Query the vector database
    results = vectordb.query(
        query_embeddings=query_embeddings,
        n_results=1  # top_k
    )

    # Prepare prompt for text generation
    system_role = "You will receive the user's question along with the search results of that question over a database. Give the user the proper answer."
    prompt = f"{system_role}\n\nUser's question: {query_texts}\n\nSearch results:\n{results}"

    # Generate response using Ollama
    response = ollama_llm.generate([prompt])

    return response.generations[0][0].text

# Initialize data when the module is imported
initialize_data()

# Example usage
if __name__ == "__main__":
    query = "what is address of dealer abc motor ?"
    result = process_and_query(query)
    print(result)