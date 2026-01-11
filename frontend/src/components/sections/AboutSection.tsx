import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Search, MessageSquareText } from 'lucide-react';

export const AboutSection: React.FC = () => {
    const steps = [
        {
            icon: <BrainCircuit size={32} />,
            title: "Ingestion",
            description: "Upload your documents (PDF, DOCX) or provide URLs. Our system processes and indexes your data instantly."
        },
        {
            icon: <Search size={32} />,
            title: "Retrieval",
            description: "When you ask a question, we find the most relevant context from your knowledge base."
        },
        {
            icon: <MessageSquareText size={32} />,
            title: "Generation",
            description: "Our advanced AI synthesizes the answer using your specific data, ensuring accuracy and relevance."
        }
    ];

    return (
        <section id="about" className="py-24 relative z-10 w-full">
            <div className="max-w-7xl mx-auto px-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-12 md:mb-16"
                >
                    <h2 className="text-3xl md:text-5xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent mb-4 md:mb-6">
                        How It Works
                    </h2>
                    <p className="text-slate-400 max-w-2xl mx-auto text-base md:text-lg leading-relaxed px-4">
                        Retrieval-Augmented Generation (RAG) combines the power of large language models with your custom data.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {steps.map((step, idx) => (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: idx * 0.2 }}
                            className="p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors group"
                        >
                            <div className="w-16 h-16 rounded-2xl bg-primary-500/20 flex items-center justify-center text-primary-300 mb-6 group-hover:scale-110 transition-transform duration-300">
                                {step.icon}
                            </div>
                            <h3 className="text-xl font-bold text-white mb-4">{step.title}</h3>
                            <p className="text-slate-400 leading-relaxed">
                                {step.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};
