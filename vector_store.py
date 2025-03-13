from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import json
import os
import argparse
import time
from tqdm import tqdm

def create_vector_store(json_file='foerderungen.json', persist_dir='./chroma_db'):
    """
    Erstellt einen Vector Store aus einer JSON-Datei mit Förderprogrammdaten
    
    Args:
        json_file: Pfad zur JSON-Datei mit den Förderprogrammdaten
        persist_dir: Verzeichnis, in dem der Vector Store gespeichert wird
    
    Returns:
        Der erstellte Vector Store
    """
    print(f"Lade Daten aus {json_file}...")
    # Load and parse JSON data
    with open(json_file, encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"{len(items)} Förderprogramme gefunden.")
    
    # Create documents with combined content
    print("Erstelle Dokumente...")
    documents = []
    for item in tqdm(items, desc="Dokumente erstellen"):
        documents.append(
            Document(
                page_content=f"{item.get('title', '')}\n{item.get('funding_details', {}).get('text', '')}",
                metadata={
                    'title': item.get('title', ''),
                    'source': item.get('referncetofdbwebsite', '')
                }
            )
        )

    # Split documents
    print("Teile Dokumente in Chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    print(f"{len(splits)} Chunks erstellt.")

    # Create vector store
    print(f"Erstelle Vector Store in {persist_dir}...")
    print("Dies kann einige Minuten dauern...")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Lösche bestehenden Vector Store, falls vorhanden
    if os.path.exists(persist_dir):
        print(f"Lösche bestehenden Vector Store in {persist_dir}...")
        import shutil
        shutil.rmtree(persist_dir)
    
    start_time = time.time()
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    end_time = time.time()
    
    print(f"Vector Store erfolgreich erstellt in {round(end_time - start_time, 2)} Sekunden!")
    return vector_store

def query_vector_store(question: str, k: int = 3, persist_dir='./chroma_db'):
    """
    Fragt den Vector Store nach relevanten Förderprogrammen ab
    
    Args:
        question: Die Frage oder Suchanfrage
        k: Anzahl der zurückzugebenden Ergebnisse
        persist_dir: Verzeichnis, in dem der Vector Store gespeichert ist
    
    Returns:
        Liste von Tupeln (Dokument, Übereinstimmungsprozent)
    """
    if not os.path.exists(persist_dir):
        raise FileNotFoundError(f"Vector Store nicht gefunden in {persist_dir}. Bitte erstellen Sie zuerst den Vector Store.")
    
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    docs = vector_store.similarity_search_with_score(question, k=k)
    # Convert cosine similarity to percentage
    return [
        (doc, min(round(100 * (1 - score / 2), 2), 100.0))  # Cosine distance [0-2] => [100%-0%]
        for doc, score in docs
    ]

def interactive_query_mode(persist_dir='./chroma_db'):
    """
    Startet einen interaktiven Abfragemodus für den Vector Store
    
    Args:
        persist_dir: Verzeichnis, in dem der Vector Store gespeichert ist
    """
    print(f"Interaktiver Abfragemodus für Vector Store in {persist_dir}")
    print("Geben Sie 'exit' ein, um zu beenden.")
    
    while True:
        try:
            question = input("\nGeben Sie eine Förderfrage ein: ")
            if question.lower() == 'exit':
                break
                
            print("Suche nach relevanten Förderprogrammen...")
            results = query_vector_store(question, persist_dir=persist_dir)
            
            print(f"\n{len(results)} relevante Programme gefunden:")
            for i, (doc, match_pct) in enumerate(results, 1):
                print(f"\n{i}. {doc.metadata['title']}")
                print(f"   Quelle: {doc.metadata['source']}")
                print(f"   Übereinstimmung: {match_pct}%")
                print(f"   {doc.page_content[:120]}...")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Fehler: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Vector Store für Förderprogramme erstellen und abfragen')
    subparsers = parser.add_subparsers(dest='command', help='Befehl')
    
    # Befehl zum Erstellen des Vector Stores
    create_parser = subparsers.add_parser('create', help='Vector Store erstellen')
    create_parser.add_argument('--input', '-i', default='foerderungen.json', help='Eingabe-JSON-Datei')
    create_parser.add_argument('--dir', '-d', default='./chroma_db', help='Vector Store Verzeichnis')
    
    # Befehl zum Abfragen des Vector Stores
    query_parser = subparsers.add_parser('query', help='Vector Store abfragen')
    query_parser.add_argument('--question', '-q', help='Frage oder Suchanfrage')
    query_parser.add_argument('--count', '-k', type=int, default=3, help='Anzahl der Ergebnisse')
    query_parser.add_argument('--dir', '-d', default='./chroma_db', help='Vector Store Verzeichnis')
    
    # Befehl für den interaktiven Abfragemodus
    interactive_parser = subparsers.add_parser('interactive', help='Interaktiver Abfragemodus')
    interactive_parser.add_argument('--dir', '-d', default='./chroma_db', help='Vector Store Verzeichnis')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_vector_store(json_file=args.input, persist_dir=args.dir)
    elif args.command == 'query':
        if not args.question:
            parser.error("Für den Befehl 'query' ist das Argument --question erforderlich")
        results = query_vector_store(args.question, k=args.count, persist_dir=args.dir)
        print(f"\n{len(results)} relevante Programme gefunden:")
        for i, (doc, match_pct) in enumerate(results, 1):
            print(f"\n{i}. {doc.metadata['title']}")
            print(f"   Quelle: {doc.metadata['source']}")
            print(f"   Übereinstimmung: {match_pct}%")
            print(f"   {doc.page_content[:120]}...")
    elif args.command == 'interactive':
        interactive_query_mode(persist_dir=args.dir)
    else:
        # Wenn kein Befehl angegeben wurde, zeige Hilfe an
        parser.print_help()
