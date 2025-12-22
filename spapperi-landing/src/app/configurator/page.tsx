'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Robot, CheckCircle, PaperPlaneRight, ArrowLeft, XCircle, DownloadSimple } from "@phosphor-icons/react";
import Link from 'next/link';
import Navbar from "@/components/Navbar";

export default function ConfiguratorPage() {
    const [hasConsented, setHasConsented] = useState(false);
    const [chatStarted, setChatStarted] = useState(false);
    const [messages, setMessages] = useState<Array<{
        role: string;
        text: string;
        image_url?: string;
        ui_type?: string;
        options?: string[];
        export_file?: string;
    }>>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [isGeneratingReport, setIsGeneratingReport] = useState(false);
    const [selectedCheckboxes, setSelectedCheckboxes] = useState<string[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load conversation ID from local storage on mount
    useEffect(() => {
        const storedId = localStorage.getItem('spapperi_conversation_id');
        if (storedId) {
            setConversationId(storedId);
            // Auto-restore chat if conversation exists
            loadExistingConversation(storedId);
        }
    }, []);

    // Auto-scroll to latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading, isGeneratingReport]);

    const loadExistingConversation = async (convId: string) => {
        // Auto-consent and start chat if conversation exists
        setHasConsented(true);
        setChatStarted(true);

        // Try to load conversation history
        try {
            const res = await fetch(`/api/conversation/${convId}/history`);
            if (res.ok) {
                const data = await res.json();
                if (data.messages && data.messages.length > 0) {
                    // Convert backend messages format to frontend
                    const formattedMessages = data.messages.map((msg: any) => ({
                        role: msg.role === 'assistant' ? 'ai' : msg.role,
                        text: msg.content,
                        image_url: msg.image_url
                    }));

                    // If conversation is complete, ensure last message has export link
                    if (data.conversation && data.conversation.is_complete && formattedMessages.length > 0) {
                        const lastMsg = formattedMessages[formattedMessages.length - 1];
                        if (lastMsg.role === 'ai') {
                            lastMsg.export_file = `/api/export/${convId}/pdf`;
                        }
                    }

                    setMessages(formattedMessages);
                    return; // Messages loaded successfully
                }
            }
        } catch (e) {
            console.error('Failed to load conversation history:', e);
        }

        // If loading fails or no messages, start fresh greeting
        fetchGreeting();
    };

    const startChat = () => {
        if (hasConsented) {
            setChatStarted(true);
            // If no messages, fetch the greeting
            if (messages.length === 0) {
                fetchGreeting();
            }
        }
    };

    const resetChat = () => {
        // Clear localStorage and reset state
        localStorage.removeItem('spapperi_conversation_id');
        setConversationId(null);
        setMessages([]);
        setChatStarted(false);
        setHasConsented(false);
    };

    const fetchGreeting = async () => {
        setIsLoading(true);
        try {
            // We send a hidden "Start" signal or just empty message to trigger the Agent's manager node
            // But the agent reacts to *last user message*.
            // If we send "Ciao" or "Start" hiddenly, the agent will reply.
            // Let's send a specific "BEGIN_SESSION" plain text, or rely on the backend recognizing a new session.
            // For now, let's send "Ciao" as a hidden bootstrap message to get the Phase 1 question.

            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: "Ciao",
                    conversation_id: conversationId
                })
            });

            if (!res.ok) throw new Error("API Error");
            const data = await res.json();

            setMessages([{
                role: 'assistant',
                text: data.response,
                image_url: data.image_url,
                ui_type: data.ui_type,
                options: data.options
            }]);

            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
                localStorage.setItem('spapperi_conversation_id', data.conversation_id);
            }

        } catch (e) {
            console.error(e);
            setMessages([{ role: 'assistant', text: "Errore di connessione. Riprova più tardi." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const closeChat = () => {
        setChatStarted(false);
    };

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMsg = inputValue;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInputValue('');

        // Detect if we should show the generation progress bar
        // Heuristic: If previous message asked for email/vat (Phase 6 trigger)
        const lastMsg = messages[messages.length - 1];
        const isFinalPhase = lastMsg && (lastMsg.role === 'assistant' || lastMsg.role === 'ai') && (
            lastMsg.text.toLowerCase().includes('email') ||
            lastMsg.text.toLowerCase().includes('partita iva') ||
            lastMsg.text.toLowerCase().includes('recapiti') ||
            lastMsg.text.toLowerCase().includes('perfetto')
        );

        if (isFinalPhase) {
            setIsGeneratingReport(true);
        }

        setIsLoading(true);

        try {
            // Securely call the Next.js API Proxy which talks to the Python Backend
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMsg,
                    conversation_id: conversationId // Send stored ID or null
                })
            });

            if (!res.ok) throw new Error("API Error");

            const data = await res.json();
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: data.response,
                image_url: data.image_url,
                ui_type: data.ui_type,
                options: data.options,
                export_file: data.export_file
            }]);

            // Persist new ID if generated
            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
                localStorage.setItem('spapperi_conversation_id', data.conversation_id);
            }

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', text: "Mi dispiace, c'è stato un problema di comunicazione con il server." }]);
        } finally {
            setIsLoading(false);
            setIsGeneratingReport(false);
        }
    };

    const sendCheckboxSelection = async () => {
        // Send selected checkboxes as JSON array
        const selectionJSON = JSON.stringify(selectedCheckboxes);

        setMessages(prev => [...prev, {
            role: 'user',
            text: selectedCheckboxes.length > 0
                ? selectedCheckboxes.join(', ')
                : 'Nessuna selezione'
        }]);
        setSelectedCheckboxes([]);
        setIsLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: selectionJSON,
                    conversation_id: conversationId
                })
            });

            if (!res.ok) throw new Error("API Error");

            const data = await res.json();
            setMessages(prev => [...prev, {
                role: 'assistant',
                text: data.response,
                image_url: data.image_url,
                ui_type: data.ui_type,
                options: data.options,
                export_file: data.export_file
            }]);

            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
                localStorage.setItem('spapperi_conversation_id', data.conversation_id);
            }

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', text: "Mi dispiace, c'è stato un problema di comunicazione con il server." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="bg-white min-h-screen text-spapperi-black font-sans relative overflow-hidden">
            {/* Navbar only visible when chat is NOT started */}
            <AnimatePresence>
                {!chatStarted && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                        className="fixed top-0 left-0 right-0 z-50"
                    >
                        <Navbar />
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence mode="wait">
                {!chatStarted ? (
                    <motion.div
                        key="intro"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
                        transition={{ duration: 0.6, ease: "circOut" }}
                        className="min-h-screen pt-32 md:pt-40 pb-12 flex flex-col px-6"
                    >
                        <div className="max-w-5xl w-full mx-auto">
                            <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-spapperi-red transition-colors mb-12 uppercase tracking-widest text-xs font-bold group">
                                <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> Torna alla Home
                            </Link>

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 mb-16 items-start">
                                <div>
                                    <h1 className="text-5xl md:text-7xl font-heading font-bold tracking-tighter leading-[0.95] mb-8">
                                        L'ingegneria<br />Spapperi,<br /><span className="text-spapperi-red">su misura per te.</span>
                                    </h1>
                                    <p className="text-xl text-spapperi-black font-light leading-relaxed max-w-lg text-justify md:text-left text-gray-600">
                                        Un percorso guidato per analizzare le tue necessità operative e individuare la tecnologia più adatta alla tua azienda.
                                    </p>
                                </div>

                                <div className="bg-gray-50 p-8 rounded-3xl border border-gray-100 relative overflow-hidden group hover:shadow-lg transition-shadow duration-500">
                                    <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity duration-500">
                                        <Robot size={120} weight="duotone" className="text-spapperi-black" />
                                    </div>
                                    <h3 className="font-heading font-bold text-xl mb-6 uppercase tracking-wider text-spapperi-black">Cosa otterrai</h3>
                                    <ul className="space-y-6 relative z-10">
                                        <li className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center shrink-0 shadow-sm text-spapperi-red">
                                                <span className="font-bold">1</span>
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-spapperi-black">Analisi Tecnica</h4>
                                                <p className="text-sm text-gray-500 leading-relaxed mt-1">Valutazione delle specifiche del terreno e delle colture.</p>
                                            </div>
                                        </li>
                                        <li className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center shrink-0 shadow-sm text-spapperi-red">
                                                <span className="font-bold">2</span>
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-spapperi-black">Configurazione Ideale</h4>
                                                <p className="text-sm text-gray-500 leading-relaxed mt-1">Identificazione del macchinario e degli accessori ottimali.</p>
                                            </div>
                                        </li>
                                        <li className="flex items-start gap-4">
                                            <div className="w-10 h-10 rounded-full bg-white border border-gray-200 flex items-center justify-center shrink-0 shadow-sm text-spapperi-red">
                                                <span className="font-bold">3</span>
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-spapperi-black">Preventivo Immediato</h4>
                                                <p className="text-sm text-gray-500 leading-relaxed mt-1">Download del report completo con costi e dettagli tecnici.</p>
                                            </div>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                            <div className="flex flex-col md:flex-row items-center justify-between gap-8 bg-white p-8 rounded-3xl border border-gray-200 shadow-sm">
                                <div className="flex items-start gap-4 max-w-md">
                                    <div className="relative flex items-center pt-1 shrink-0">
                                        <input
                                            type="checkbox"
                                            id="gdpr"
                                            checked={hasConsented}
                                            onChange={(e) => setHasConsented(e.target.checked)}
                                            className="peer h-6 w-6 cursor-pointer appearance-none rounded-lg border-2 border-gray-300 transition-all checked:border-spapperi-red checked:bg-spapperi-red hover:border-spapperi-red"
                                        />
                                        <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white opacity-0 transition-opacity peer-checked:opacity-100 mt-0.5">
                                            <CheckCircle size={14} weight="fill" />
                                        </div>
                                    </div>
                                    <label htmlFor="gdpr" className="text-sm text-gray-500 hover:text-spapperi-black cursor-pointer select-none leading-relaxed transition-colors">
                                        Per procedere, confermo di aver preso visione dei <a href="#" className="font-bold underline text-spapperi-black hover:text-spapperi-red">Termini di Servizio</a> e della <a href="#" className="font-bold underline text-spapperi-black hover:text-spapperi-red">Privacy Policy</a> di Spapperi NT S.r.l.
                                    </label>
                                </div>

                                <button
                                    onClick={startChat}
                                    disabled={!hasConsented}
                                    className={`group flex items-center gap-3 px-10 py-5 text-sm font-bold uppercase tracking-widest rounded-full transition-all duration-300 shrink-0
                                        ${hasConsented
                                            ? 'bg-spapperi-black text-white hover:bg-spapperi-red hover:gap-5 hover:shadow-xl hover:scale-105 active:scale-95'
                                            : 'bg-gray-100 text-gray-300 cursor-not-allowed'
                                        }`}
                                >
                                    Inizia Configurazione
                                    <PaperPlaneRight size={18} weight="fill" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="chat"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ duration: 0.5, ease: "circOut" }}
                        className="h-screen pt-12 pb-8 px-4 flex flex-col max-w-4xl mx-auto relative"
                    >
                        {/* Close Button */}
                        <button
                            onClick={closeChat}
                            className="absolute top-8 right-8 text-gray-400 hover:text-spapperi-red transition-colors z-50 p-2"
                        >
                            <XCircle size={40} weight="duotone" />
                        </button>

                        <div className="flex-1 overflow-y-auto space-y-6 mb-8 scrollbar-hide pt-12">
                            {messages.map((msg, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`max-w-[80%] p-6 rounded-3xl text-lg font-medium leading-relaxed
                                        ${msg.role === 'user'
                                            ? 'bg-spapperi-red text-white rounded-br-none shadow-lg'
                                            : 'bg-gray-100 text-gray-800 rounded-bl-none'
                                        }`}
                                    >
                                        {msg.text}
                                        {msg.image_url && (
                                            <div className="mt-4 rounded-lg overflow-hidden border border-gray-200">
                                                <img
                                                    src={`http://localhost:8000${msg.image_url}`}
                                                    alt="Riferimento configurazione"
                                                    className="w-full h-auto"
                                                />
                                            </div>

                                        )}

                                        {msg.export_file && (
                                            <div className="mt-6">
                                                <a
                                                    href={`http://localhost:8000${msg.export_file}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="group inline-flex items-center gap-3 bg-spapperi-black text-white px-8 py-4 rounded-full font-bold uppercase tracking-widest text-sm hover:bg-spapperi-red hover:gap-5 transition-all duration-300 shadow-md"
                                                >
                                                    <DownloadSimple size={20} weight="bold" />
                                                    Scarica Report PDF
                                                </a>
                                            </div>
                                        )}

                                        {/* Checkbox/Radio UI for selections */}
                                        {(msg.ui_type === 'checkbox' || msg.ui_type === 'radio') && msg.options && msg.role === 'assistant' && (
                                            <div className="mt-4 space-y-3">
                                                {msg.options.map((option, idx) => (
                                                    <label
                                                        key={idx}
                                                        className="flex items-center gap-3 p-3 rounded-lg bg-white hover:bg-gray-50 cursor-pointer transition-colors border border-gray-200"
                                                    >
                                                        <input
                                                            type="checkbox"
                                                            checked={selectedCheckboxes.includes(option)}
                                                            onChange={(e) => {
                                                                if (msg.ui_type === 'radio') {
                                                                    // Single selection for radio
                                                                    setSelectedCheckboxes(e.target.checked ? [option] : []);
                                                                } else {
                                                                    // Multi selection for checkbox
                                                                    if (e.target.checked) {
                                                                        setSelectedCheckboxes(prev => [...prev, option]);
                                                                    } else {
                                                                        setSelectedCheckboxes(prev => prev.filter(item => item !== option));
                                                                    }
                                                                }
                                                            }}
                                                            className="w-5 h-5 text-spapperi-red rounded focus:ring-2 focus:ring-spapperi-red"
                                                        />
                                                        <span className="text-gray-700 font-medium">{option}</span>
                                                    </label>
                                                ))}

                                                <button
                                                    onClick={sendCheckboxSelection}
                                                    disabled={isLoading || selectedCheckboxes.length === 0}
                                                    className="mt-4 w-full bg-spapperi-red text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    {isLoading ? 'Invio...' : 'Conferma Selezione'}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}

                            {/* Loading State: Progress Bar OR Typing Indicator */}
                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0 }}
                                    className="flex justify-start w-full"
                                >
                                    {isGeneratingReport ? (
                                        /* Premium Progress Bar UI for Final Generation */
                                        <div className="bg-white border border-gray-100 shadow-md p-6 rounded-3xl rounded-bl-none w-full max-w-md">
                                            <div className="flex items-center gap-4 mb-4">
                                                <div className="animate-spin text-spapperi-red">
                                                    <Robot size={24} weight="duotone" />
                                                </div>
                                                <span className="font-bold text-spapperi-black uppercase tracking-wider text-sm">
                                                    Generazione Configurazione
                                                </span>
                                            </div>
                                            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                                <motion.div
                                                    className="h-full bg-spapperi-red"
                                                    initial={{ width: "0%" }}
                                                    animate={{ width: "100%" }}
                                                    transition={{ duration: 8, ease: "easeInOut" }}
                                                />
                                            </div>
                                            <p className="text-xs text-gray-400 mt-3 font-medium">L'AI sta elaborando il report tecnico e il preventivo...</p>
                                        </div>
                                    ) : (
                                        /* Standard Typing Indicator */
                                        <div className="bg-gray-100 p-6 rounded-3xl rounded-bl-none">
                                            <div className="flex gap-1.5">
                                                <motion.div
                                                    animate={{ y: [0, -8, 0] }}
                                                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                                                    className="w-2.5 h-2.5 bg-gray-400 rounded-full"
                                                />
                                                <motion.div
                                                    animate={{ y: [0, -8, 0] }}
                                                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                                                    className="w-2.5 h-2.5 bg-gray-400 rounded-full"
                                                />
                                                <motion.div
                                                    animate={{ y: [0, -8, 0] }}
                                                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                                                    className="w-2.5 h-2.5 bg-gray-400 rounded-full"
                                                />
                                            </div>
                                        </div>
                                    )}
                                </motion.div>
                            )}

                            {/* Scroll anchor */}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="relative">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder="Scrivi qui..."
                                disabled={isLoading}
                                className="w-full bg-white border-2 border-gray-100 rounded-full py-6 pl-8 pr-20 text-xl focus:outline-none focus:border-spapperi-red focus:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                autoFocus
                            />
                            <button
                                onClick={sendMessage}
                                disabled={isLoading}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-spapperi-black text-white rounded-full flex items-center justify-center hover:bg-spapperi-red transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <PaperPlaneRight size={24} weight="fill" />
                            </button>
                        </div>
                    </motion.div>
                )
                }
            </AnimatePresence >
        </main >
    );
}
