import React from 'react';
import ShaderBackground from '@/components/ui/shader-background';
import { HeroSection } from '@/components/ui/hero-section';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { AboutSection } from '@/components/sections/AboutSection';
import { SupportedDocsSection } from '@/components/sections/SupportedDocsSection';
import { AppWorkspace } from '@/components/sections/AppWorkspace';

function App() {
  const handleGetStarted = () => {
    const workspace = document.getElementById('workspace');
    if (workspace) {
      workspace.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen font-sans text-slate-900 flex flex-col relative overflow-x-hidden">
      <ShaderBackground />
      <Header />

      <main className="flex-1 w-full">
        <HeroSection onGetStarted={handleGetStarted} />
        <AboutSection />
        <SupportedDocsSection />
        <AppWorkspace />
      </main>

      <Footer />
    </div>
  );
}

export default App;
