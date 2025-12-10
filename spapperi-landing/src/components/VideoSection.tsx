'use client';

export default function VideoSection() {
    return (
        <section className="relative w-full h-[80vh] bg-white overflow-hidden flex items-center justify-center">

            {/* Container - No shadows, no rounding for seamless integration */}
            <div className="relative w-full h-full max-w-full mx-auto overflow-hidden">
                <iframe
                    className="w-full h-full object-cover scale-125 pointer-events-none"
                    src="https://www.youtube.com/embed/UvoO500jYSs?autoplay=1&mute=1&controls=0&loop=1&playlist=UvoO500jYSs&rel=0&showinfo=0&modestbranding=1&iv_load_policy=3"
                    title="Spapperi TC12 AM"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerPolicy="strict-origin-when-cross-origin"
                    allowFullScreen
                ></iframe>

                {/* Aggressive Seamless Fades */}
                {/* Top Fade */}
                <div className="absolute top-0 left-0 w-full h-48 bg-gradient-to-b from-white via-white/80 to-transparent z-10 pointer-events-none"></div>
                {/* Bottom Fade */}
                <div className="absolute bottom-0 left-0 w-full h-48 bg-gradient-to-t from-white via-white/80 to-transparent z-10 pointer-events-none"></div>


            </div>

        </section>
    );
}
