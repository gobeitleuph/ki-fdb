# Funding Data Vector Store

## Overview
This application provides a semantic search interface for funding programs using vector embeddings. It consists of:

1. **Vector Store Backend**: Python-based system that loads funding data, creates embeddings, and enables semantic search
2. **FastAPI Server**: Exposes the vector store functionality through a REST API
3. **Next.js Frontend**: Modern chat interface for querying funding programs with percentage match visualization

## Docker Compose Setup (Empfohlen)

Die einfachste Methode, die Anwendung zu starten, ist mit Docker Compose:

1. Stellen Sie sicher, dass Docker und Docker Compose installiert sind:
```bash
docker --version
docker-compose --version
```

2. Bauen und starten Sie die Container:
```bash
docker-compose up -d --build
```

3. Öffnen Sie Ihren Browser und navigieren Sie zu http://localhost:3000

4. Um die Container zu stoppen:
```bash
docker-compose down
```

5. Um die Logs anzuzeigen:
```bash
docker-compose logs -f
```

6. Um nur die Logs eines bestimmten Dienstes anzuzeigen:
```bash
docker-compose logs -f backend
# oder
docker-compose logs -f frontend
```

### Fehlerbehebung

- Falls der Frontend-Container nicht starten kann, stellen Sie sicher, dass der Backend-Container läuft und gesund ist:
```bash
docker-compose ps
```

- Falls Änderungen am Code vorgenommen wurden, bauen Sie die Container neu:
```bash
docker-compose up -d --build
```

- Um die Container und Volumes zu entfernen (Achtung: Dies löscht alle Daten):
```bash
docker-compose down -v
```

## Backend Setup (Manuelle Installation)
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your JSON data in `foerderungen.json` with format:
```json
{
    "data": [
        {
            "title": "Program Name",
            "description": "Detailed description...",
            "eligibility": "Eligibility criteria..."
        }
    ]
}
```

3. Create the vector store:
```bash
python vector_store.py
```

The system will:
- Load and chunk JSON data
- Create embeddings using all-MiniLM-L6-v2 model
- Store vectors in ChromaDB (local .chroma_db directory)

4. Start the FastAPI server:
```bash
python api.py
```

## Vector Store Verwendung

Der Vector Store kann mit verschiedenen Pfaden verwendet werden. Dies ermöglicht es, mehrere Vector Stores für verschiedene Datensätze zu erstellen und zu verwenden.

### Vector Store erstellen

```bash
python vector_store.py create --input foerderungen.json --dir ./chroma_db
```

Parameter:
- `--input` oder `-i`: Pfad zur JSON-Datei (Standard: foerderungen.json)
- `--dir` oder `-d`: Verzeichnis für den Vector Store (Standard: ./chroma_db)

### Vector Store abfragen

```bash
python vector_store.py query --question "Ihre Frage hier" --dir ./chroma_db
```

Parameter:
- `--question` oder `-q`: Die Frage oder Suchanfrage (erforderlich)
- `--count` oder `-k`: Anzahl der Ergebnisse (Standard: 3)
- `--dir` oder `-d`: Verzeichnis des Vector Stores (Standard: ./chroma_db)

### Interaktiven Abfragemodus starten

```bash
python vector_store.py interactive --dir ./chroma_db
```

Parameter:
- `--dir` oder `-d`: Verzeichnis des Vector Stores (Standard: ./chroma_db)

### API-Verwendung

Die API unterstützt ebenfalls die Angabe eines benutzerdefinierten Vector Store Pfades:

```json
POST /api/suche
{
  "query": "Ihre Frage hier",
  "limit": 3,
  "vector_store_path": "./chroma_db"
}
```

Parameter:
- `query`: Die Frage oder Suchanfrage (erforderlich)
- `limit`: Anzahl der Ergebnisse (optional, Standard: 3)
- `vector_store_path`: Pfad zum Vector Store (optional, Standard: ./chroma_db)

## Frontend Setup (Manuelle Installation)
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Using the Application
1. Ensure both backend and frontend servers are running:
   - Backend: `python api.py` (running on http://localhost:8000)
   - Frontend: `npm run dev` in the frontend directory (running on http://localhost:3000)

2. Open your browser and navigate to http://localhost:3000

3. Use the chat interface to query funding programs:
   - Type your question in the input field
   - Results will display with percentage match scores and star ratings
   - Click on source links to view original program details

## Features
- **Semantic Search**: Find relevant funding programs based on meaning, not just keywords
- **Percentage Matching**: See how well each result matches your query
- **Visual Rating**: Star system provides quick visual feedback on match quality
- **Modern UI**: Clean, responsive interface following the design styleguide

## Technical Details
- **Vector Embeddings**: SentenceTransformers for semantic representation
- **Vector Store**: ChromaDB for efficient similarity search
- **API**: FastAPI for backend services
- **Frontend**: Next.js with Tailwind CSS for styling
- **UI Components**: Framer Motion for animations, Heroicons for icons

```bash
python xml_processor.py foerderleistungen --output foerderungen.json
```

```bash
python vector_store.py
```

```bash
python vector_store.py create --input foerderungen.json --dir ./chroma_db
```

```bash
python vector_store.py query --question "Ihre Frage hier"       
```

```bash
python vector_store.py interactive --dir ./chroma_db