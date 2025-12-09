import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import HorizontalScrollFeatures from "@/components/HorizontalScrollFeatures";
import TechSpecs from "@/components/TechSpecs";
import Footer from "@/components/Footer";
import SmoothScroll from "@/components/SmoothScroll";
import VideoSection from "@/components/VideoSection";
import TwoColumnCTA from "@/components/TwoColumnCTA";

export default function Home() {
  return (
    <SmoothScroll>
      <main className="bg-white min-h-screen">
        <Navbar />
        <Hero />
        <VideoSection />
        <HorizontalScrollFeatures />
        <TechSpecs />
        <TwoColumnCTA />
        <Footer />
      </main>
    </SmoothScroll>
  );
}
