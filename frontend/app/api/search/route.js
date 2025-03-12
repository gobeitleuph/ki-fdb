export async function POST(request) {
  try {
    const body = await request.json();
    
    // API-URL aus Umgebungsvariable oder Fallback
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Forward the request to our FastAPI backend
    const response = await fetch(`${apiUrl}/api/suche`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`Backend-Fehler: ${response.status}`);
    }
    
    const data = await response.json();
    return new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('API-Routenfehler:', error);
    return new Response(
      JSON.stringify({ error: error.message || 'Anfrage konnte nicht verarbeitet werden' }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
}
