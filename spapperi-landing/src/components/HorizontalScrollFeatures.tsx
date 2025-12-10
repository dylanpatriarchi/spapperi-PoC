'use client';

import { useRef, useEffect } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Aperture, Lightning, Gear, Stack, ArrowRight } from '@phosphor-icons/react';

gsap.registerPlugin(ScrollTrigger);

const features = [
    { icon: <Aperture weight="duotone" className="w-12 h-12" />, title: "Distributore Rotante 12", desc: "Sistema brevettato a 12 tazze ad apertura orizzontale. Ideale per zolle coniche, cilindriche e piramidali fino a 3cm di diametro." },
    { icon: <Lightning weight="duotone" className="w-12 h-12" />, title: "Produzione Record", desc: "Capacità produttiva media di 4.500 piantine/ora per fila. Prestazioni elevate senza compromettere la precisione di posa." },
    { icon: <Gear weight="duotone" className="w-12 h-12" />, title: "Twin Drive System", desc: "Trasmissione con coppia ruote motrici laterali e barra esagonale. Garantisce trazione costante su ogni tipo di terreno." },
    { icon: <Stack weight="duotone" className="w-12 h-12" />, title: "Modularità Totale", desc: "Telaio configurabile da 1 a 6 file con interfila minima di 45cm. Disponibile in versioni Fissi (TF), Telescopici (TT) e Pieghevoli (TP)." },
];

export default function HorizontalScrollFeatures() {
    const sectionRef = useRef<HTMLDivElement>(null);
    const trackRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        let ctx = gsap.context(() => {
            const track = trackRef.current;
            if (track) {
                gsap.to(track, {
                    x: () => -(track.scrollWidth - window.innerWidth),
                    ease: "none",
                    scrollTrigger: {
                        trigger: sectionRef.current,
                        pin: true,
                        scrub: 1,
                        end: () => "+=" + (track.scrollWidth - window.innerWidth),
                        invalidateOnRefresh: true,
                    }
                });
            }
        }, sectionRef);

        return () => ctx.revert();
    }, []);

    return (
        <section ref={sectionRef} className="relative h-screen bg-white overflow-hidden flex flex-col justify-center border-t border-gray-100">

            <div className="absolute top-12 left-12 md:left-24 z-10 w-full max-w-lg pointer-events-none">
                <h2 className="text-spapperi-black text-6xl md:text-7xl font-heading font-bold uppercase tracking-tight leading-none">
                    Tech <span className="text-spapperi-red">Insights</span>
                </h2>
            </div>

            <div ref={trackRef} className="flex gap-16 px-12 md:px-24 w-fit items-center h-full pt-20">
                {features.map((f, i) => (
                    <div key={i} className="w-[85vw] md:w-[70vw] h-[60vh] flex flex-col justify-between p-16 bg-white border-l border-gray-200 relative shrink-0 group hover:bg-gray-50 transition-colors duration-500">

                        {/* Top: Number & Icon */}
                        <div className="flex justify-between items-start">
                            <span className="font-heading text-6xl md:text-9xl font-bold text-gray-100 group-hover:text-gray-200 transition-colors -ml-4 -mt-4">
                                0{i + 1}
                            </span>
                            <div className="p-4 md:p-6 bg-red-50 text-spapperi-red rounded-full group-hover:scale-110 transition-transform duration-500">
                                {f.icon}
                            </div>
                        </div>

                        {/* Bottom: Content */}
                        <div className="mt-auto">
                            <h3 className="text-3xl md:text-6xl font-heading font-bold text-spapperi-black mb-4 md:mb-8 uppercase tracking-tight leading-none group-hover:translate-x-2 transition-transform duration-500">
                                {f.title}
                            </h3>
                            <div className="w-24 h-1 bg-spapperi-red mb-8"></div>
                            <p className="text-gray-500 text-xl md:text-2xl font-sans font-light leading-relaxed max-w-3xl">
                                {f.desc}
                            </p>
                            <div className="mt-8 flex items-center gap-4 text-spapperi-black font-bold uppercase tracking-widest text-sm opacity-0 group-hover:opacity-100 transform translate-y-4 group-hover:translate-y-0 transition-all duration-500">
                                Scopri di più <ArrowRight size={20} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
}
