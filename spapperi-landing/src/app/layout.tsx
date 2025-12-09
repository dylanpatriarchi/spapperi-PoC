import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TC12 RTD REAR - Spapperi",
  description: "Elemento di trapianto con distributore ruotante. Innovazione allo stato puro.",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="it">
      <body
        className={`antialiased font-sans bg-white text-spapperi-black`}
      >
        {children}
      </body>
    </html>
  );
}
