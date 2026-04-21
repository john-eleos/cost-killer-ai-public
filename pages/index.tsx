import React, { useState } from 'react';
import Head from 'next/head';

export default function SavingsDashboard() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [savings, setSavings] = useState(0);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const handleTest = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          messages: [{ role: 'user', content: prompt }],
          license_key: "USER_PRIMARY" 
        }),
      });
      const data = await res.json();
      
      setResponse(data);
      if (data.metadata?.savings) {
        const numericSavings = parseFloat(data.metadata.savings.replace('$', ''));
        setSavings(prev => prev + numericSavings);
      }
      setHistory(prev => [data, ...prev].slice(0, 5));
    } catch (error) {
      console.error("Routing error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-zinc-100 font-sans selection:bg-blue-500/30">
      <Head>
        <title>Cost-Killer AI | Dashboard</title>
      </Head>

      {/* Top Nav */}
      <nav className="border-b border-zinc-800 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white tracking-tighter">
              CK
            </div>
            <span className="font-bold text-lg tracking-tight text-white">Cost-Killer <span className="text-zinc-500">AI</span></span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium text-zinc-400 uppercase tracking-widest">
            <a href="#" className="hover:text-blue-400 transition-colors">Infrastructure</a>
            <a href="#" className="hover:text-blue-400 transition-colors">Analytics</a>
            <button className="bg-zinc-800 text-white px-4 py-1.5 rounded-full hover:bg-zinc-700 transition-all border border-zinc-700 text-xs">
              v5.0.0
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-12 gap-10">
          
          {/* Sidebar Metrics */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl backdrop-blur-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <svg className="w-24 h-24 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
              </div>
              <h3 className="text-zinc-500 text-xs font-bold uppercase tracking-widest mb-1">Total Savings</h3>
              <div className="text-6xl font-mono font-bold text-blue-500 tracking-tighter tabular-nums">
                ${savings.toFixed(4)}
              </div>
              <p className="text-zinc-500 text-sm mt-4 leading-relaxed">
                Calculated efficiency gain vs. top-tier models (GPT-4o/Claude-Opus).
              </p>
            </div>

            <div className="bg-zinc-900/50 border border-zinc-800 p-8 rounded-3xl space-y-4">
              <h3 className="text-zinc-500 text-xs font-bold uppercase tracking-widest">Recent Optimization</h3>
              {history.length > 0 ? (
                <div className="space-y-3">
                  {history.map((item, i) => (
                    <div key={i} className="flex items-center justify-between text-xs border-b border-zinc-800 pb-2 last:border-0">
                      <span className="text-zinc-400 truncate w-32">{item.metadata?.model}</span>
                      <span className="text-blue-500 font-mono">+{item.metadata?.savings}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-600 text-xs italic">No telemetry data yet.</p>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="col-span-12 lg:col-span-8 space-y-8">
            
            {/* Input Section */}
            <div className="space-y-4">
              <div className="relative group">
                <textarea 
                  className="w-full bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 h-48 text-lg focus:border-blue-500/50 focus:ring-4 focus:ring-blue-500/5 outline-none transition-all placeholder:text-zinc-700 resize-none leading-relaxed"
                  placeholder="Paste a complex task here..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                />
                <div className="absolute bottom-6 right-6">
                  <button 
                    onClick={handleTest}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 text-white font-bold px-8 py-3 rounded-2xl transition-all shadow-xl shadow-blue-500/10 flex items-center gap-2 group/btn"
                  >
                    {loading ? (
                      <span className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                        <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                        <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce"></span>
                      </span>
                    ) : (
                      <>
                        Run Routing 
                        <svg className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M13 7l5 5m0 0l-5 5m5-5H6"/></svg>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Output Section */}
            {response && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-2xl">
                  <div className="px-8 py-4 border-b border-zinc-800 bg-zinc-900/80 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">Response</span>
                      <div className="flex gap-1.5">
                        <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
                        <div className="w-2 h-2 rounded-full bg-yellow-500/50"></div>
                        <div className="w-2 h-2 rounded-full bg-green-500/50"></div>
                      </div>
                    </div>
                    <div className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-1 rounded">
                      {response.metadata?.model}
                    </div>
                  </div>
                  <div className="p-8 font-mono text-sm leading-relaxed text-zinc-300 max-h-[500px] overflow-y-auto whitespace-pre-wrap">
                    {response.content}
                  </div>
                  <div className="px-8 py-4 border-t border-zinc-800 bg-zinc-900/50 flex items-center gap-10">
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-zinc-600 uppercase">Savings</span>
                      <span className="text-blue-500 font-bold">{response.metadata?.savings}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-zinc-600 uppercase">Latency</span>
                      <span className="text-zinc-400 font-bold">{response.metadata?.latency}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-zinc-600 uppercase">Cache</span>
                      <span className={`font-bold ${response.metadata?.cache === 'HIT' ? 'text-green-500' : 'text-zinc-500'}`}>
                        {response.metadata?.cache}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto px-6 py-20 border-t border-zinc-900 flex justify-between items-center text-zinc-600">
        <div className="text-xs">
          Built by <span className="text-zinc-400 font-bold">Gemini CLI</span> | Orchestrated via <span className="text-zinc-400 font-bold">LiteLLM</span>
        </div>
        <div className="flex gap-8 text-xs font-medium uppercase tracking-widest">
          <a href="#" className="hover:text-white transition-colors">GitHub</a>
          <a href="#" className="hover:text-white transition-colors">Documentation</a>
          <a href="#" className="hover:text-white transition-colors">Twitter</a>
        </div>
      </footer>
    </div>
  );
}
