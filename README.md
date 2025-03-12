# Funding Data Vector Store

## Setup
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

3. Run processing:
```bash
python vector_store.py
```

The system will:
- Load and chunk JSON data
- Create embeddings using all-MiniLM-L6-v2 model
- Store vectors in ChromaDB (local .chroma_db directory)
