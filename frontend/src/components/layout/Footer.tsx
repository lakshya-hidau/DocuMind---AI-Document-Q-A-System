import React from 'react';
import { motion } from 'framer-motion';
import { Twitter, Linkedin, Youtube, Instagram, Share2 } from 'lucide-react';

export const Footer: React.FC = () => {
    return (
        <footer className="w-full relative bg-slate-950 pt-20 pb-10 overflow-hidden border-t border-white/5">
            {/* Massive Background Text with Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full pointer-events-none select-none overflow-hidden">
                <motion.h2
                    initial={{ opacity: 0.03, scale: 0.95 }}
                    whileHover={{ opacity: 0.08, scale: 1.02 }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="text-[6rem] md:text-[20rem] font-bold text-center leading-none tracking-tighter text-white"
                    style={{
                        WebkitTextStroke: '1px rgba(255, 255, 255, 0.1)',
                        textShadow: '0 0 40px rgba(6, 182, 212, 0.2)'
                    }}
                >
                    DocuMind
                </motion.h2>
            </div>

            {/* Content Container */}
            <div className="max-w-7xl mx-auto px-6 relative z-10">
                {/* Visual Divider / Glow Line */}
                <div className="w-full h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent mb-12"></div>

                <div className="flex flex-col md:flex-row justify-between items-center gap-8">
                    {/* Left Side: Copyright & Links */}
                    <div className="flex flex-col md:flex-row items-center gap-4 md:gap-8 text-slate-500 text-xs font-medium">
                        <p>© 2026 DocuMind Inc.</p>
                        <div className="flex gap-6">
                            <a href="#" className="hover:text-cyan-400 transition-colors uppercase tracking-widest">Sitemap</a>
                            <a href="#" className="hover:text-cyan-400 transition-colors uppercase tracking-widest">Legal Center</a>
                        </div>
                    </div>

                    {/* Right Side: Social Icons */}
                    <div className="flex items-center gap-5 text-slate-400">
                        <motion.a
                            whileHover={{ y: -3, color: '#fff' }}
                            href="#"
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                            aria-label="X (Twitter)"
                        >
                            <Twitter size={18} />
                        </motion.a>
                        <motion.a
                            whileHover={{ y: -3, color: '#fff' }}
                            href="#"
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                            aria-label="LinkedIn"
                        >
                            <Linkedin size={18} />
                        </motion.a>
                        <motion.a
                            whileHover={{ y: -3, color: '#fff' }}
                            href="#"
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                            aria-label="YouTube"
                        >
                            <Youtube size={18} />
                        </motion.a>
                        <motion.a
                            whileHover={{ y: -3, color: '#fff' }}
                            href="#"
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                            aria-label="Instagram"
                        >
                            <Instagram size={18} />
                        </motion.a>
                        <motion.a
                            whileHover={{ y: -3, color: '#fff' }}
                            href="#"
                            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 transition-all"
                            aria-label="Reddit"
                        >
                            <Share2 size={18} />
                        </motion.a>
                    </div>
                </div>

                {/* Bottom branding detail */}
                <div className="mt-12 text-center text-[10px] text-slate-700 uppercase tracking-[0.5em] font-bold">
                    Advanced AI Document Intelligence Platform
                </div>
            </div>
        </footer>
    );
};
