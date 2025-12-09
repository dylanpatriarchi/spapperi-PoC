export default function TechnicalIcon({ children }: { children: React.ReactNode }) {
    return (
        <div className="relative w-16 h-16 flex items-center justify-center border border-spapperi-black/20 bg-gray-50/50 backdrop-blur-sm">
            {/* Corner Markers */}
            <div className="absolute top-0 left-0 w-2 h-2 border-l border-t border-spapperi-red"></div>
            <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-spapperi-red"></div>
            <div className="absolute bottom-0 left-0 w-2 h-2 border-l border-b border-spapperi-red"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 border-r border-b border-spapperi-red"></div>

            {/* Center Crosshair */}
            <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
                <div className="w-full h-px bg-spapperi-black"></div>
                <div className="h-full w-px bg-spapperi-black absolute"></div>
            </div>

            <div className="relative z-10 text-spapperi-black">
                {children}
            </div>
        </div>
    );
}
