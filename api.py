from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import uvicorn
from vector_store import query_vector_store

app = FastAPI(title="Fördermittel-Finder API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 3

class ResultItem(BaseModel):
    title: str
    source: str
    match: float
    content: str

@app.post("/api/suche", response_model=List[ResultItem])
async def suche(request: QueryRequest):
    try:
        # Query the vector store
        results = query_vector_store(request.query, k=request.limit)
        
        # Format the results
        formatted_results = []
        for doc, match_pct in results:
            formatted_results.append(
                ResultItem(
                    title=doc.metadata.get("title", "Ohne Titel"),
                    source=doc.metadata.get("source", ""),
                    match=match_pct,
                    content=doc.page_content[:300]  # Limit content length
                )
            )
        
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ein interner Serverfehler ist aufgetreten")

@app.get("/api/status")
async def status_prüfung():
    return {"status": "gesund"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
