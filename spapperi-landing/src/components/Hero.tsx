'use client';

import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { SplitText } from './SplitText';
import Scene from './Scene';

export default function Hero() {
    const containerRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const tl = gsap.timeline();

        // Initial clear
        gsap.set(containerRef.current, { visibility: 'visible' });

        tl.to('.char', {
            y: 0,
            opacity: 1,
            stagger: 0.05,
            duration: 0.8,
            ease: 'power3.out'
        });

    }, []);

    return (
        <section ref={containerRef} className="relative min-h-[90vh] flex items-center pt-24 pb-12 overflow-hidden bg-gradient-to-br from-white to-gray-50 invisible">
            {/* Abstract Background Elements */}
            <div className="absolute top-0 right-0 w-1/3 h-full bg-gray-100/50 skew-x-12 translate-x-32 -z-10"></div>

            <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">

                <div className="z-10 order-2 lg:order-1">
                    <div className="inline-block px-4 py-1.5 mb-6 bg-red-50 border border-red-100 rounded-full">
                        <span className="text-spapperi-red font-bold tracking-wider text-xs uppercase">Nuova Tecnologia RTD</span>
                    </div>

                    <h1 className="text-6xl md:text-8xl lg:text-9xl font-heading font-bold text-spapperi-black mb-8 leading-[0.9] uppercase tracking-tighter">
                        <div className="flex flex-col">
                            <SplitText text="TC12 RTD" className="inline-block" delay={0.2} />
                            <span className="text-spapperi-red opacity-100">REAR</span>
                        </div>
                    </h1>

                    <p className="text-neutral-500 font-sans text-lg md:text-xl max-w-lg mb-12 leading-relaxed tracking-tight border-l-4 border-spapperi-red pl-6">
                        Elemento di trapianto con distributore ruotante.
                        Innovazione pura.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-0">
                        <button className="bg-spapperi-red text-white px-10 py-5 font-bold hover:bg-black transition-all hover:shadow-2xl text-center cursor-pointer uppercase tracking-widest text-sm rounded-l-full rounded-r-none">
                            Specifiche Tecniche
                        </button>
                        <button className="group border-2 border-l-0 border-neutral-200 text-neutral-800 px-10 py-5 font-bold hover:bg-neutral-50 transition-all flex items-center justify-center gap-2 cursor-pointer uppercase tracking-widest text-sm bg-white rounded-r-full rounded-l-none">
                            <span>Datasheet</span>
                            <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                        </button>
                    </div>
                </div>

                <div className="order-1 lg:order-2 relative h-[50vh] lg:h-[80vh] w-full flex justify-center items-center">
                    <div className="absolute inset-0 bg-gradient-to-tr from-gray-100 to-white opacity-50 rounded-full blur-3xl transform scale-75"></div>
                    <Scene />
                </div>

            </div>
        </section>
    );
}
