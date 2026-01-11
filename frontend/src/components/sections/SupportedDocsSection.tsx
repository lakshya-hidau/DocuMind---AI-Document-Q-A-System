import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Link2, FileType, Shield, Cpu, Zap } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, desc, delay }: { icon: any, title: string, desc: string, delay: number }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay }}
        className="bg-slate-800/50 border border-white/10 rounded-2xl p-8 hover:bg-slate-800/80 transition-all hover:-translate-y-1 shadow-lg"
    >
        <div className="w-14 h-14 bg-primary-600/20 text-primary-400 rounded-xl flex items-center justify-center mb-6">
            <Icon size={32} />
        </div>
        <h3 className="text-2xl font-bold text-white mb-4">{title}</h3>
        <p className="text-slate-300 text-lg leading-relaxed">{desc}</p>
    </motion.div>
);

export const SupportedDocsSection: React.FC = () => {
    return (
        <section id="features" className="py-24 relative z-10 w-full bg-slate-900/30">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-12 md:mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-4 md:mb-6">
                        Powerful Features
                    </h2>
                    <p className="text-base md:text-xl text-slate-400 max-w-2xl mx-auto px-4">
                        Everything you need to analyze your documents effectively.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={FileType}
                        title="Drag & Drop Files"
                        desc="Easily upload PDF, Word (DOCX), and Text files. We parse and index everything instantly."
                        delay={0.1}
                    />
                    <FeatureCard
                        icon={Link2}
                        title="Web Links"
                        desc="Paste any URL. We'll scrape the content and make it chat-ready in seconds."
                        delay={0.2}
                    />
                    <FeatureCard
                        icon={Cpu}
                        title="Smart AI Model"
                        desc="Powered by Llama-3-8B for high-quality, reasoning-based answers."
                        delay={0.3}
                    />
                    <FeatureCard
                        icon={Shield}
                        title="Private Sessions"
                        desc="Your data is isolated. Each session is a fresh, secure environment."
                        delay={0.4}
                    />
                    <FeatureCard
                        icon={Zap}
                        title="Instant Context"
                        desc="Our vector engine finds the exact paragraphs needed to answer your query."
                        delay={0.5}
                    />
                    <FeatureCard
                        icon={FileText}
                        title="Source Citations"
                        desc="AI references the specific parts of your document used for the answer."
                        delay={0.6}
                    />
                </div>
            </div>
        </section>
    );
};
