'use client';

import Image from "next/image";
import { ArrowRight, Robot, Wrench } from "@phosphor-icons/react";

export default function TwoColumnCTA() {
    return (
        <section className="bg-white py-24 px-6 md:px-12 lg:px-24">
            <div className="max-w-screen-2xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 h-[600px]">

                {/* Card 1: AI Configurator */}
                <div className="group relative w-full h-full rounded-2xl overflow-hidden cursor-pointer">
                    <div className="absolute inset-0">
                        <Image
                            src="/banner_trapiantatrici.png"
                            alt="AI Configurator"
                            fill
                            className="object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                    </div>

                    <div className="absolute bottom-0 left-0 p-12 w-full">
                        <div className="flex items-center gap-4 mb-4 text-spapperi-red">
                            <Robot size={48} weight="duotone" />
                            <span className="text-sm font-bold tracking-widest uppercase bg-white/10 backdrop-blur-md px-3 py-1 rounded-full border border-white/20 text-white">
                                Nuovo
                            </span>
                        </div>
                        <h3 className="text-4xl md:text-5xl font-heading font-bold text-white mb-6 leading-[0.9] tracking-tighter">
                            Configura la tua<br />trapiantatrice con l'AI.
                        </h3>
                        <div className="flex items-center gap-4 text-white font-medium group-hover:gap-6 transition-all duration-300">
                            <span>Inizia ora</span>
                            <ArrowRight size={24} />
                        </div>
                    </div>
                </div>

                {/* Card 2: Spare Parts */}
                <div className="group relative w-full h-full rounded-2xl overflow-hidden cursor-pointer">
                    <div className="absolute inset-0">
                        <Image
                            src="/ricambi_spapperi.jpg"
                            alt="Spapperi Spare Parts"
                            fill
                            className="object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                    </div>

                    <div className="absolute bottom-0 left-0 p-12 w-full">
                        <div className="text-spapperi-red mb-4">
                            <Wrench size={48} weight="duotone" />
                        </div>
                        <h3 className="text-4xl md:text-5xl font-heading font-bold text-white mb-6 leading-[0.9] tracking-tighter">
                            Ricambi per le tue<br />macchine Spapperi.
                        </h3>
                        <div className="flex items-center gap-4 text-white font-medium group-hover:gap-6 transition-all duration-300">
                            <span>Vai allo shop</span>
                            <ArrowRight size={24} />
                        </div>
                    </div>
                </div>

            </div>
        </section>
    );
}
