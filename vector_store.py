from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import json

def create_vector_store():
    # Load and parse JSON data
    with open('foerderungen.json', encoding='utf-8') as f:
        items = json.load(f)
    
    # Create documents with combined content
    documents = [
        Document(
            page_content=f"{item.get('title', '')}\n{item.get('funding_details', {}).get('text', '')}",
            metadata={
                'title': item.get('title', ''),
                'source': item.get('referncetofdbwebsite', '')
            }
        )
        for item in items
    ]

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    # Create vector store
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    return vector_store

def query_vector_store(question: str, k: int = 3):
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )
    docs = vector_store.similarity_search_with_score(question, k=k)
    # Convert cosine similarity to percentage
    return [
        (doc, min(round(100 * (1 - score / 2), 2), 100.0))  # Cosine distance [0-2] => [100%-0%]
        for doc, score in docs
    ]

if __name__ == "__main__":
    while True:
        try:
            question = input("\nEnter funding question (or 'exit'): ")
            if question.lower() == 'exit':
                break
            results = query_vector_store(question)
            print(f"\nFound {len(results)} relevant programs:")
            for i, (doc, match_pct) in enumerate(results, 1):
                print(f"\n{i}. {doc.metadata['title']}")
                print(f"   Source: {doc.metadata['source']}")
                print(f"   Match: {match_pct}% {'★'*int(match_pct/20)} {doc.page_content[:120]}...")
        except KeyboardInterrupt:
            break
