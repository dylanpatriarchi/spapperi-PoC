'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Robot, CheckCircle, PaperPlaneRight, ArrowLeft, XCircle } from "@phosphor-icons/react";
import Link from 'next/link';
import Image from 'next/image';
import Navbar from "@/components/Navbar";

export default function ConfiguratorPage() {
    const [hasConsented, setHasConsented] = useState(false);
    const [chatStarted, setChatStarted] = useState(false);
    const [messages, setMessages] = useState<Array<{ role: string, text: string, image_url?: string }>>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);

    // Load conversation ID from local storage on mount
    useEffect(() => {
        const storedId = localStorage.getItem('spapperi_conversation_id');
        if (storedId) setConversationId(storedId);
    }, []);

    const startChat = () => {
        if (hasConsented) {
            setChatStarted(true);
            // If no messages, fetch the greeting
            if (messages.length === 0) {
                fetchGreeting();
            }
        }
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

            setMessages([{ role: 'ai', text: data.response, image_url: data.image_url }]);

            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
                localStorage.setItem('spapperi_conversation_id', data.conversation_id);
            }

        } catch (e) {
            console.error(e);
            setMessages([{ role: 'ai', text: "Errore di connessione. Riprova più tardi." }]);
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
            setMessages(prev => [...prev, { role: 'ai', text: data.response, image_url: data.image_url }]);

            // Persist new ID if generated
            if (data.conversation_id && data.conversation_id !== conversationId) {
                setConversationId(data.conversation_id);
                localStorage.setItem('spapperi_conversation_id', data.conversation_id);
            }

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'ai', text: "Mi dispiace, c'è stato un problema di comunicazione con il server." }]);
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
                        <div className="max-w-2xl w-full mx-auto">
                            <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-spapperi-red transition-colors mb-12 uppercase tracking-widest text-xs font-bold group">
                                <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> Torna alla Home
                            </Link>

                            <div className="mb-12">
                                <div className="w-16 h-16 bg-gray-50 rounded-xl flex items-center justify-center mb-8">
                                    <Robot size={32} weight="duotone" className="text-spapperi-red" />
                                </div>
                                <h1 className="text-5xl md:text-7xl font-heading font-bold tracking-tighter leading-[0.9] mb-8">
                                    Spapperi<br /><span className="text-spapperi-red">AI Logic.</span>
                                </h1>
                                <p className="text-xl text-spapperi-black font-light leading-relaxed max-w-lg text-justify md:text-left">
                                    Configura la tua macchina ideale dialogando con la nostra Intelligenza Artificiale.
                                    Risparmia tempo e ottieni una soluzione su misura.
                                </p>
                            </div>

                            <div className="bg-white p-8 rounded-2xl border border-gray-200 mb-12 shadow-sm">
                                <h3 className="font-heading font-bold text-lg mb-6 uppercase tracking-wider text-spapperi-black">Istruzioni</h3>
                                <ul className="space-y-4 text-spapperi-black font-medium mb-8">
                                    <li className="flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-spapperi-red mt-2.5 shrink-0"></div>
                                        <span>L'IA ti farà domande sulle tue esigenze (coltura, terreno, dimensioni).</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <div className="w-1.5 h-1.5 rounded-full bg-spapperi-red mt-2.5 shrink-0"></div>
                                        <span>Potrai scaricare la configurazione finale in PDF.</span>
                                    </li>
                                </ul>

                                <div className="flex items-start gap-4 pt-6 border-t border-gray-100">
                                    <div className="relative flex items-center pt-1">
                                        <input
                                            type="checkbox"
                                            id="gdpr"
                                            checked={hasConsented}
                                            onChange={(e) => setHasConsented(e.target.checked)}
                                            className="peer h-5 w-5 cursor-pointer appearance-none rounded border-2 border-gray-300 transition-all checked:border-spapperi-red checked:bg-spapperi-red hover:border-spapperi-red"
                                        />
                                        <div className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-white opacity-0 transition-opacity peer-checked:opacity-100 mt-0.5">
                                            <CheckCircle size={12} weight="fill" />
                                        </div>
                                        {hasConsented && (
                                            <CheckCircle size={20} weight="fill" className="absolute top-0.5 left-0 text-spapperi-red pointer-events-none" />
                                        )}
                                    </div>
                                    <label htmlFor="gdpr" className="text-sm text-gray-500 hover:text-spapperi-black cursor-pointer select-none leading-relaxed transition-colors">
                                        Accetto i <a href="#" className="font-bold underline text-spapperi-black hover:text-spapperi-red">Termini di Servizio</a> e la <a href="#" className="font-bold underline text-spapperi-black hover:text-spapperi-red">Privacy Policy</a>.
                                    </label>
                                </div>
                            </div>

                            <button
                                onClick={startChat}
                                disabled={!hasConsented}
                                className={`group flex items-center gap-3 px-8 py-4 text-sm font-bold uppercase tracking-widest rounded-full transition-all duration-300
                                    ${hasConsented
                                        ? 'bg-spapperi-black text-white hover:bg-spapperi-red hover:gap-5'
                                        : 'bg-gray-100 text-gray-300 cursor-not-allowed'
                                    }`}
                            >
                                Avvia Chat
                                <PaperPlaneRight size={18} weight="fill" />
                            </button>
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
                                                <Image
                                                    src={msg.image_url}
                                                    alt="Riferimento configurazione"
                                                    width={400}
                                                    height={300}
                                                    className="w-full h-auto"
                                                    unoptimized
                                                />
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        <div className="relative">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder="Scrivi qui..."
                                className="w-full bg-white border-2 border-gray-100 rounded-full py-6 pl-8 pr-20 text-xl focus:outline-none focus:border-spapperi-red focus:shadow-xl transition-all"
                                autoFocus
                            />
                            <button
                                onClick={sendMessage}
                                className="absolute right-3 top-1/2 -translate-y-1/2 w-12 h-12 bg-spapperi-black text-white rounded-full flex items-center justify-center hover:bg-spapperi-red transition-colors"
                            >
                                <PaperPlaneRight size={24} weight="fill" />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </main>
    );
}
