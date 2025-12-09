'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { MagnifyingGlass } from "@phosphor-icons/react";

export default function Navbar() {
    const navRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        gsap.fromTo(navRef.current,
            { y: -100, opacity: 0 },
            { y: 0, opacity: 1, duration: 1, ease: "power4.out", delay: 0.5 }
        );
    }, []);

    return (
        <nav ref={navRef} className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-fit rounded-full bg-white/60 backdrop-blur-2xl border border-white/20 shadow-xl overflow-hidden px-6 py-3 flex justify-center items-center gap-8 text-spapperi-black font-sans">

            {/* Brand */}
            <Link href="/" className="relative h-6 w-32 hover:opacity-80 transition-opacity">
                <Image src="/logo_spapperi.svg" alt="Spapperi" fill className="object-contain object-left" />
            </Link>

            {/* Links */}
            <ul className="hidden md:flex gap-8 text-sm font-medium tracking-wide">
                <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Prodotti</li>
                <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Azienda</li>
                <li className="hover:text-spapperi-red cursor-pointer transition-colors uppercase">Servizi</li>
            </ul>

            {/* Action */}
            <button className="p-2 hover:bg-white/50 rounded-full transition-colors text-spapperi-black hover:text-spapperi-red">
                <MagnifyingGlass size={24} weight="bold" />
            </button>

        </nav>
    );
}
