'use client';
import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

export default function ChatInterface() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
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
      const response = await fetch('/api/suche', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: currentQuery })
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

  return (
    <div className="min-h-screen bg-[#F2F2F2] p-4">
      <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[#646464]/20 bg-[#1E466E] text-white rounded-t-xl">
          <h1 className="text-xl font-bold">
            Fördermittel-Finder
          </h1>
          <p className="text-sm mt-1 opacity-80">
          </p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center text-[#646464]/50">
              <p>Stellen Sie eine Frage zu Förderprogrammen</p>
            </div>
          )}
          
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[80%] p-3 rounded-lg ${
                msg.type === 'user' 
                  ? 'bg-[#1E466E] text-white'
                  : msg.type === 'error'
                    ? 'bg-[#DC3545] text-white'
                    : 'bg-[#F2F2F2] border border-[#646464]/10'
              }`}
              >
                {msg.type === 'user' && (
                  <p>{msg.content}</p>
                )}
                
                {msg.type === 'error' && (
                  <p>{msg.content}</p>
                )}
                
                {msg.type === 'bot' && msg.results && (
                  <div className="space-y-4">
                    {msg.results.map((result, idx) => (
                      <div key={idx} className="border-b border-[#646464]/10 pb-3 last:border-b-0 last:pb-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[#1E466E] font-bold">
                            {idx + 1}. {result.title}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2 mb-2 text-xs">
                          <a
                            href={result.source}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#05C3DC] underline"
                          >
                            Quelle
                          </a>
                          <span className="text-[#646464]">
                            Übereinstimmung: {result.match}%
                          </span>
                        </div>
                        
                        <p className="text-[#646464] text-sm">
                          {result.content}...
                        </p>
                      </div>
                    ))}
                    
                    {msg.results.length === 0 && (
                      <p className="text-[#646464] italic">Keine passenden Programme gefunden</p>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSearch} className="p-4 border-t border-[#646464]/20">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Beispiel: Ich möchte maritime Forschung betreiben..."
              className="flex-1 p-2 border border-[#646464]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#05C3DC] text-sm"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-[#1E466E] text-white p-2 rounded-lg hover:bg-[#0F2A45] disabled:opacity-50 transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <PaperAirplaneIcon className="w-5 h-5" />
              )}
              <span className="hidden sm:inline">Senden</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
