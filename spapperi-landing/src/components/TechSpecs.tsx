'use client';

const specs = [
    {
        category: "Dotazioni di serie",
        items: [
            "Parallelogramma per oscillazione elemento",
            "Sistema di distribuzione ruotante a 12 bicchieri",
            "Sedile imbottito con schienale",
            "Predisposizione Twin Drive / Roll Drive"
        ]
    },
    {
        category: "Trasmissioni",
        items: [
            "Twin Drive: Ruote motrici + barra",
            "Roll Drive: Rulli gommati + barra"
        ]
    },
    {
        category: "Telai",
        items: [
            "Fissi (2 tubi) / Maxi (4 tubi)",
            "Rettangolari / Maxi Rettangolari",
            "Telescopici / Pieghevoli"
        ]
    },
    {
        category: "Allestimenti",
        items: [
            "1–4 file (Twin Drive)",
            "1–6 file (Roll Drive)",
            "File aggiuntive su richiesta"
        ]
    },
    {
        category: "Accessori",
        items: [
            "Micro granulatore / Spandiconcime",
            "Innaffiamento localizzato",
            "Porta piante girevoli"
        ]
    },
    {
        category: "Dati Tecnici",
        items: [
            "Prod: 4000 piante/h per fila",
            "Interfila: 47 ÷ 198 cm",
            "Interpianta: 10 ÷ 56 cm",
            "Interbina: 104 ÷ 148 cm"
        ]
    }
];

export default function TechSpecs() {
    return (
        <section id="tech-specs" className="py-32 bg-white border-t border-gray-100 text-spapperi-black relative overflow-hidden">
            {/* Subtle background grid */}
            <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03] pointer-events-none"></div>

            <div className="container mx-auto px-6 relative z-10">
                <div className="mb-20 text-center">
                    <span className="text-spapperi-red font-sans font-bold text-xs tracking-[0.3em] uppercase mb-6 block">Datasheet // 01</span>
                    <h2 className="text-6xl md:text-8xl font-heading font-bold uppercase tracking-tighter mb-4">
                        Specifiche <span className="opacity-30">Tecniche</span>
                    </h2>
                </div>

                <div className="grid md:grid-cols-3 gap-0 border-t border-b border-gray-200 divide-x divide-gray-200">
                    {specs.map((cat, i) => (
                        <div key={i} className="group relative p-12 hover:bg-gray-50 transition-colors duration-500">
                            {/* Technical Crosshairs (Light Mode) */}
                            <div className="absolute top-4 left-4 w-2 h-2 border-l border-t border-gray-300 group-hover:border-spapperi-red transition-colors"></div>
                            <div className="absolute bottom-4 right-4 w-2 h-2 border-r border-b border-gray-300 group-hover:border-spapperi-red transition-colors"></div>

                            <div className="text-7xl font-heading font-bold text-gray-100 absolute top-4 right-4 select-none group-hover:text-gray-200 transition-colors">
                                0{i + 1}
                            </div>

                            <h3 className="text-3xl font-heading font-bold mb-8 relative z-10 uppercase tracking-wide text-spapperi-black">
                                {cat.category}
                            </h3>

                            <ul className="space-y-4 relative z-10">
                                {cat.items.map((item, j) => (
                                    <li key={j} className="flex items-center gap-4 text-lg font-sans text-gray-500 group-hover:text-spapperi-black transition-colors font-medium">
                                        <div className="w-1.5 h-1.5 bg-gray-300 group-hover:bg-spapperi-red rounded-none transform rotate-45 transition-colors"></div>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                <div className="mt-20 text-center">
                    <button className="bg-spapperi-red text-white px-8 py-4 sm:px-12 sm:py-5 font-bold text-sm sm:text-lg uppercase tracking-widest hover:bg-spapperi-black hover:shadow-xl transition-all duration-300 shadow-lg cursor-pointer whitespace-nowrap">
                        Scarica PDF <span className="hidden sm:inline ml-2">[ 2.4 MB ]</span>
                    </button>
                </div>
            </div>
        </section>
    );
}
