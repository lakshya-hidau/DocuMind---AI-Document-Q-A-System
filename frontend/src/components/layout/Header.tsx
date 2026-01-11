import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Github, Menu, X } from 'lucide-react';

export const Header: React.FC = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
        setIsMenuOpen(false);
    };

    const navLinks = [
        { name: 'How it Works', id: 'about' },
        { name: 'Features', id: 'features' },
    ];

    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed top-0 left-0 right-0 z-50 px-6 py-4 backdrop-blur-lg bg-slate-900/50 border-b border-white/10"
        >
            <div className="max-w-7xl mx-auto flex items-center justify-between">
                <div
                    className="flex items-center space-x-3 text-white font-bold text-xl cursor-pointer group"
                    onClick={() => {
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        setIsMenuOpen(false);
                    }}
                >
                    <img
                        src="/icon.svg"
                        alt="DocuMind Logo"
                        className="h-10 w-10 transition-transform group-hover:scale-110"
                    />
                    <span className="text-white drop-shadow-[0_0_10px_rgba(139,92,246,0.6)] group-hover:drop-shadow-[0_0_15px_rgba(139,92,246,0.8)] transition-all">DocuMind</span>
                </div>

                {/* DESKTOP NAV */}
                <nav className="hidden md:flex items-center space-x-8 text-slate-300 text-sm font-medium">
                    {navLinks.map(link => (
                        <button
                            key={link.id}
                            onClick={() => scrollToSection(link.id)}
                            className="hover:text-white transition-colors"
                        >
                            {link.name}
                        </button>
                    ))}
                    <button onClick={() => scrollToSection('workspace')} className="px-5 py-2.5 bg-primary-600 hover:bg-primary-500 text-white rounded-full transition-all shadow-lg shadow-primary-900/20 active:scale-95">
                        Try It Now
                    </button>
                    <a href="https://github.com/lakshya-hidau/DocuMind---AI-Document-Q-A-System" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
                        <Github size={22} />
                    </a>
                </nav>

                {/* MOBILE MENU TOGGLE */}
                <div className="flex items-center gap-4 md:hidden">
                    <a href="https://github.com/lakshya-hidau/DocuMind---AI-Document-Q-A-System" target="_blank" rel="noopener noreferrer" className="text-slate-300 hover:text-white transition-colors">
                        <Github size={22} />
                    </a>
                    <button
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        className="p-2 text-slate-300 hover:text-white transition-colors"
                    >
                        {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
                    </button>
                </div>
            </div>

            {/* MOBILE NAV OVERLAY */}
            <AnimatePresence>
                {isMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden mt-4 pt-4 border-t border-white/10 flex flex-col space-y-4 pb-4 overflow-hidden"
                    >
                        {navLinks.map(link => (
                            <button
                                key={link.id}
                                onClick={() => scrollToSection(link.id)}
                                className="text-left text-lg text-slate-300 hover:text-white transition-colors px-2 py-1"
                            >
                                {link.name}
                            </button>
                        ))}
                        <button
                            onClick={() => scrollToSection('workspace')}
                            className="w-full py-4 bg-primary-600 hover:bg-primary-500 text-white rounded-2xl font-bold transition-all text-center"
                        >
                            Try It Now
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.header>
    );
};
