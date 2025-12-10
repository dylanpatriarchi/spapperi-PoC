'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { MagnifyingGlass, List, X } from "@phosphor-icons/react";
import { AnimatePresence, motion } from 'framer-motion';

export default function Navbar() {
    const navRef = useRef<HTMLDivElement>(null);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        gsap.fromTo(navRef.current,
            { y: -100, x: "-50%", opacity: 0 },
            { y: 0, x: "-50%", opacity: 1, duration: 1, ease: "power4.out", delay: 0.5 }
        );
    }, []);

    const toggleMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

    return (
        <>
            <nav ref={navRef} className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[90%] md:w-fit rounded-3xl bg-white/60 backdrop-blur-2xl border border-white/20 shadow-xl overflow-visible px-6 py-3 flex justify-between md:justify-center items-center gap-8 text-spapperi-black font-sans transition-all duration-300">

                {/* Brand */}
                <Link href="/" className="relative h-6 w-32 hover:opacity-80 transition-opacity shrink-0">
                    <Image src="/logo_spapperi.svg" alt="Spapperi" fill className="object-contain object-left" />
                </Link>

                {/* Desktop Links */}
                <ul className="hidden md:flex gap-8 text-sm font-medium tracking-wide items-center">
                    <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Prodotti</li>
                    <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Azienda</li>
                    <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Servizi</li>
                </ul>

                {/* Actions (Desktop + Mobile Toggle) */}
                <div className="flex items-center gap-4">
                    <button className="p-2 hover:bg-white/50 rounded-full transition-colors text-spapperi-black hover:text-spapperi-red hidden md:block">
                        <MagnifyingGlass size={24} weight="bold" />
                    </button>

                    {/* Mobile Menu Toggle */}
                    <button onClick={toggleMenu} className="p-1 md:hidden text-spapperi-black hover:text-spapperi-red transition-colors">
                        {isMobileMenuOpen ? <X size={24} weight="bold" /> : <List size={24} weight="bold" />}
                    </button>
                </div>

            </nav>

            {/* Mobile Menu Overlay */}
            <AnimatePresence>
                {isMobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                        className="fixed top-24 left-1/2 -translate-x-1/2 w-[90%] bg-white/90 backdrop-blur-xl border border-white/20 shadow-2xl rounded-3xl z-40 p-6 md:hidden flex flex-col gap-6 items-center text-center"
                    >
                        <ul className="flex flex-col gap-6 text-lg font-bold tracking-wide w-full">
                            <li onClick={toggleMenu} className="hover:text-spapperi-red cursor-pointer transition-colors uppercase py-2 border-b border-gray-100 w-full">Prodotti</li>
                            <li onClick={toggleMenu} className="hover:text-spapperi-red cursor-pointer transition-colors uppercase py-2 border-b border-gray-100 w-full">Azienda</li>
                            <li onClick={toggleMenu} className="hover:text-spapperi-red cursor-pointer transition-colors uppercase py-2 border-b border-gray-100 w-full">Servizi</li>
                        </ul>
                        <button className="flex items-center gap-2 p-3 bg-gray-100 rounded-full w-full justify-center text-spapperi-black hover:bg-spapperi-red hover:text-white transition-all font-bold uppercase text-sm">
                            <MagnifyingGlass size={20} weight="bold" />
                            <span>Cerca</span>
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
