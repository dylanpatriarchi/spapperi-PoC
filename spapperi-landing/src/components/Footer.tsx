'use client';

import { FacebookLogo, InstagramLogo, YoutubeLogo, LinkedinLogo, ArrowUpRight } from "@phosphor-icons/react";
import Image from "next/image";

export default function Footer() {
    return (
        <footer className="bg-white text-spapperi-black py-24 px-6 md:px-12 lg:px-24 border-t border-gray-100">
            <div className="max-w-screen-2xl mx-auto">

                {/* Top: Big CTA */}
                <div className="border-b border-gray-100 pb-24 mb-24">
                    <div className="mb-12 relative w-[80vw] h-[15vw] md:h-[8vw] max-w-4xl">
                        <Image
                            src="/logo_spapperi.svg"
                            alt="Spapperi"
                            fill
                            className="object-contain object-left"
                        />
                    </div>
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-12">
                        <p className="max-w-xl text-2xl md:text-3xl text-gray-500 font-light font-sans">
                            Ridefinisci i tuoi standard di trapianto con la tecnologia TC12. Precisione assoluta, zero compromessi.
                        </p>
                        <button className="group relative px-12 py-6 bg-spapperi-black text-white font-bold text-lg uppercase tracking-widest overflow-hidden hover:bg-spapperi-red transition-colors duration-300">
                            <span className="relative z-10 flex items-center gap-4">
                                Contattaci <ArrowUpRight size={24} />
                            </span>
                        </button>
                    </div>
                </div>

                {/* Middle: Links Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-16 mb-24 font-sans">
                    <div>
                        <h4 className="text-gray-400 uppercase tracking-widest text-sm mb-8 font-bold">Azienda</h4>
                        <ul className="space-y-4 text-xl font-medium">
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Chi Siamo</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Storia</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Sostenibilità</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Lavora con noi</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-gray-400 uppercase tracking-widest text-sm mb-8 font-bold">Prodotti</h4>
                        <ul className="space-y-4 text-xl font-medium">
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Trapiantatici</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Pacciamatici</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Sarchiatrici</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Configuratore</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-gray-400 uppercase tracking-widest text-sm mb-8 font-bold">Supporto</h4>
                        <ul className="space-y-4 text-xl font-medium">
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Ricambi</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Assistenza Tecnica</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Manuali</a></li>
                            <li><a href="#" className="hover:text-spapperi-red transition-colors">Contatti</a></li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-gray-400 uppercase tracking-widest text-sm mb-8 font-bold">Social</h4>
                        <div className="flex gap-6 text-spapperi-black">
                            <a href="#" className="hover:text-spapperi-red transition-colors"><FacebookLogo size={32} weight="fill" /></a>
                            <a href="#" className="hover:text-spapperi-red transition-colors"><InstagramLogo size={32} weight="fill" /></a>
                            <a href="#" className="hover:text-spapperi-red transition-colors"><YoutubeLogo size={32} weight="fill" /></a>
                            <a href="#" className="hover:text-spapperi-red transition-colors"><LinkedinLogo size={32} weight="fill" /></a>
                        </div>
                    </div>
                </div>

                {/* Bottom: Copyright */}
                <div className="border-t border-gray-100 pt-12 flex flex-col md:flex-row justify-between items-center text-gray-400 font-sans text-sm tracking-wide">
                    <p>&copy; 2025 Dylan Patriarchi. All Rights Reserved.</p>
                    <div className="flex gap-8 mt-4 md:mt-0">
                        <a href="#" className="hover:text-spapperi-black transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-spapperi-black transition-colors">Cookie Policy</a>
                        <a href="#" className="hover:text-spapperi-black transition-colors">Terms of Use</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
