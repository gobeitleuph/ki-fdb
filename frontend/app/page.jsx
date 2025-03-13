'use client';
import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [vectorStorePath, setVectorStorePath] = useState('./chroma_db');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message
    const userMessage = { type: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    
    // Clear input and set loading
    const currentQuery = query;
    setQuery('');
    setIsLoading(true);
    
    try {
      // Call API
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: currentQuery,
          vector_store_path: vectorStorePath 
        })
      });
      
      if (!response.ok) {
        throw new Error(`Fehler ${response.status}: ${response.statusText}`);
      }
      
      const results = await response.json();
      
      // Add bot message with results
      setMessages(prev => [...prev, { 
        type: 'bot', 
        results: results 
      }]);
    } catch (error) {
      console.error('Suchfehler:', error);
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: `Fehler beim Abrufen der Ergebnisse: ${error.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handler für Änderungen am Vector Store Pfad
  const handleVectorStorePathChange = (e) => {
    setVectorStorePath(e.target.value);
  };

  return (
    <div className="min-h-screen bg-[#F2F2F2] p-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#1A1A1A] mb-2">Fördermittel-Finder</h1>
          <p className="text-[#4D4D4D]">Stellen Sie eine Frage zu Förderprogrammen</p>
        </header>

        {/* Vector Store Pfad Eingabe */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <label htmlFor="vectorStorePath" className="block text-sm font-medium text-[#4D4D4D] mb-2">
            Vector Store Pfad:
          </label>
          <input
            type="text"
            id="vectorStorePath"
            value={vectorStorePath}
            onChange={handleVectorStorePathChange}
            className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="./chroma_db"
          />
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <div className="h-[60vh] overflow-y-auto mb-4">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-[#4D4D4D]">
                <p className="mb-2">Willkommen beim Fördermittel-Finder!</p>
                <p className="text-sm">Stellen Sie eine Frage zu verfügbaren Förderprogrammen.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message, index) => (
                  <div key={index}>
                    {message.type === 'user' && (
                      <div className="flex justify-end">
                        <div className="bg-blue-500 text-white rounded-lg py-2 px-4 max-w-[80%]">
                          {message.content}
                        </div>
                      </div>
                    )}
                    
                    {message.type === 'bot' && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg py-3 px-4 max-w-[80%]">
                          {message.results.length > 0 ? (
                            <div>
                              <p className="font-medium mb-2">Hier sind einige relevante Förderprogramme:</p>
                              <div className="space-y-4">
                                {message.results.map((result, idx) => (
                                  <div key={idx} className="border-b pb-2 last:border-b-0">
                                    <p className="font-medium">{result.title}</p>
                                    <p className="text-sm text-[#4D4D4D] mb-1">
                                      Übereinstimmung: {result.match}%
                                    </p>
                                    {result.source && (
                                      <a 
                                        href={result.source} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="text-xs text-blue-500 hover:underline block mb-1"
                                      >
                                        Mehr Informationen
                                      </a>
                                    )}
                                    <p className="text-sm">{result.content}...</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <p>Leider wurden keine passenden Förderprogramme gefunden.</p>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {message.type === 'error' && (
                      <div className="flex justify-start">
                        <div className="bg-red-100 text-red-700 rounded-lg py-2 px-4 max-w-[80%]">
                          {message.content}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
          
          <form onSubmit={handleSearch} className="flex items-center">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Frage zu Förderprogrammen eingeben..."
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-blue-500 text-white p-3 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <PaperAirplaneIcon className="w-6 h-6" />
              )}
            </button>
          </form>
        </div>
        
        <footer className="text-center text-sm text-[#4D4D4D]">
          <p> 2025 Fördermittel-Finder</p>
        </footer>
      </div>
    </div>
  );
}
