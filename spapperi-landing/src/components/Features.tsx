'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Activity, Move, Settings, Layers, CheckCircle } from 'lucide-react';
import SpotlightCard from './SpotlightCard';

gsap.registerPlugin(ScrollTrigger);

const features = [
    { icon: <Activity className="w-6 h-6" />, title: "Precisione Estrema", desc: "Sistema di distribuzione ruotante a 12 bicchieri per una posa perfetta." },
    { icon: <Move className="w-6 h-6" />, title: "Adattabilità", desc: "Parallelogramma per oscillazione indipendente dell'elemento." },
    { icon: <Settings className="w-6 h-6" />, title: "Versatile", desc: "Adatto a piantine con cubetto conico o piramidale." },
    { icon: <Layers className="w-6 h-6" />, title: "Seduta Comfort", desc: "Sedile imbottito con schienale per lunghe sessioni di lavoro." },
];

const transmissions = [
    { title: "Twin Drive", desc: "Coppia di ruote motrici con barra di trasmissione fra gli elementi." },
    { title: "Roll Drive", desc: "Rulli motrici gommati con barra di trasmissione fra gli elementi." },
];

export default function Features() {
    const scrollRef = useRef(null);

    useEffect(() => {
        const ctx = gsap.context(() => {
            gsap.from(".feature-card", {
                scrollTrigger: {
                    trigger: scrollRef.current,
                    start: "top 80%",
                },
                y: 50,
                opacity: 0,
                duration: 0.8,
                stagger: 0.1,
            });
        }, scrollRef);
        return () => ctx.revert();
    }, []);

    return (
        <section ref={scrollRef} className="py-24 bg-white relative">
            <div className="container mx-auto px-6">
                <div className="text-center max-w-2xl mx-auto mb-16">
                    <h2 className="text-sm font-bold text-spapperi-red tracking-widest uppercase mb-2">Caratteristiche</h2>
                    <h3 className="text-3xl md:text-4xl font-heading font-bold text-spapperi-black">Innovazione al Servizio dell'Agricoltura</h3>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((f, i) => (
                        <SpotlightCard key={i} className="p-8 h-full bg-gray-50/50 backdrop-blur-sm">
                            <div className="feature-card h-full flex flex-col">
                                <div className="bg-white w-14 h-14 rounded-full flex items-center justify-center text-spapperi-red shadow-sm mb-6 group-hover:bg-spapperi-red group-hover:text-white transition-colors duration-300">
                                    {f.icon}
                                </div>
                                <h4 className="text-xl font-bold text-spapperi-black mb-3">{f.title}</h4>
                                <p className="text-gray-600 leading-relaxed text-sm">{f.desc}</p>
                            </div>
                        </SpotlightCard>
                    ))}
                </div>

                <div className="mt-24 grid md:grid-cols-2 gap-12 items-center bg-[#151515] rounded-3xl p-8 md:p-12 text-white overflow-hidden relative shadow-2xl">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-spapperi-red opacity-5 rounded-full blur-3xl translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>

                    <div className="z-10">
                        <h3 className="text-3xl font-heading font-bold mb-6">Sistemi di Trasmissione</h3>
                        <p className="text-gray-400 mb-8 max-w-md">Scegli la configurazione più adatta al tuo terreno per massimizzare la produttività.</p>
                        <div className="space-y-6">
                            {transmissions.map((t, i) => (
                                <div key={i} className="flex gap-4">
                                    <CheckCircle className="w-6 h-6 text-spapperi-red shrink-0" />
                                    <div>
                                        <h4 className="font-bold text-lg text-white">{t.title}</h4>
                                        <p className="text-gray-500 text-sm">{t.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="relative h-64 bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl flex items-center justify-center border border-gray-800 overflow-hidden group">
                        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
                        <span className="text-gray-500 font-mono text-xs uppercase tracking-widest z-10 group-hover:text-white transition-colors">Visualizzazione 3D in arrivo</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
