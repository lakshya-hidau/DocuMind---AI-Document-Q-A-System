import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import DocumentUpload from '../DocumentUpload';
import ChatInterface from '../ChatInterface';
import { Button } from '@/components/ui/button';
import { RefreshCcw, Server, Cpu, FileText, Link as LinkIcon, File as FileIcon, Eye, EyeOff, LayoutPanelLeft } from 'lucide-react';

// Extracted component to handle Object URL lifecycle and prevent re-renders
const FilePreview: React.FC<{ content: File | string, type: 'file' | 'url' | 'text', name: string }> = ({ content, type, name }) => {
    const [objectUrl, setObjectUrl] = useState<string | null>(null);

    useEffect(() => {
        if (type === 'file' && content instanceof File) {
            const url = URL.createObjectURL(content);
            setObjectUrl(url);
            return () => {
                URL.revokeObjectURL(url);
            };
        }
        setObjectUrl(null);
    }, [content, type]);

    if (type === 'file' && content instanceof File) {
        if (name.toLowerCase().endsWith('.pdf') && objectUrl) {
            return (
                <div className="flex-1 min-h-0 w-full overflow-hidden bg-white rounded-xl border border-white/20 shadow-inner flex flex-col">
                    <iframe src={objectUrl} className="w-full flex-1" title="PDF Preview" />
                </div>
            );
        }
        return (
            <div className="flex-1 min-h-0 flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-900/50 rounded-xl border border-white/5">
                <FileIcon size={48} className="mb-4 text-slate-500" />
                <p className="mb-2 text-white font-medium">Preview Unavailable</p>
                <p className="text-sm">This file type cannot be previewed directly.</p>
            </div>
        );
    }

    if (type === 'url' && typeof content === 'string') {
        return (
            <div className="flex-1 w-full h-full flex flex-col gap-2">
                <div className="flex-1 min-h-0 w-full h-[45vh] md:h-full bg-white rounded-xl overflow-hidden border border-white/20 relative shadow-inner">
                    <iframe src={content} className="w-full h-full" title="Web Preview" />
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    asChild
                    className="w-full bg-slate-800 border-white/10 text-slate-300 hover:text-white"
                >
                    <a href={content} target="_blank" rel="noopener noreferrer">
                        <LinkIcon size={14} className="mr-2" /> Open in New Tab
                    </a>
                </Button>
            </div>
        );
    }

    if (type === 'text' && typeof content === 'string') {
        return (
            <div className="flex-1 min-h-0 w-full h-full bg-slate-950/50 rounded-xl overflow-hidden border border-white/20 flex flex-col">
                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                    <pre className="text-slate-300 font-mono text-sm whitespace-pre-wrap break-words">{content}</pre>
                </div>
            </div>
        );
    }

    return null;
};

export const AppWorkspace: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [activeDoc, setActiveDoc] = useState<{ name: string; type: 'file' | 'url' | 'text'; content: File | string } | null>(null);
    const [showSidebar, setShowSidebar] = useState(true);

    // Auto-hide sidebar on mobile after session creation
    const handleSessionCreated = (id: string, name: string, type: 'file' | 'url' | 'text', content: File | string) => {
        setSessionId(id);
        setActiveDoc({ name, type, content });
        if (window.innerWidth < 768) {
            setShowSidebar(false);
        }
    };

    const handleReset = () => {
        setSessionId(null);
        setActiveDoc(null);
        setShowSidebar(true);
    };

    return (
        <section id="workspace" className="min-h-screen relative z-10 w-full flex flex-col items-center justify-center py-8 px-4 bg-slate-900/20">
            <div className="w-full max-w-7xl">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="flex flex-col md:flex-row items-start md:items-end justify-between mb-8 gap-4"
                >
                    <div>
                        <h2 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
                            <LayoutPanelLeft className="text-cyan-400" />
                            Control Center
                        </h2>
                        <p className="text-slate-400">Upload documents and start intelligent conversations.</p>
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-[10px] md:text-xs font-mono font-bold text-white bg-slate-950/50 px-4 md:px-6 py-3 rounded-2xl border border-white/10 shadow-xl backdrop-blur-md">
                        <span className="flex items-center gap-2 text-emerald-400">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            ONLINE
                        </span>
                        <span className="hidden sm:block text-white/20">|</span>
                        <span className="flex items-center gap-2 text-sky-300">
                            <Server size={14} /> {sessionId ? 'ACTIVE' : 'READY'}
                        </span>
                        <span className="hidden sm:block text-white/20">|</span>
                        <span className="flex items-center gap-2 text-violet-300">
                            <Cpu size={14} /> LLAMA-3.2
                        </span>
                    </div>
                </motion.div>

                <div className="relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-cyan-500 rounded-3xl opacity-20 group-hover:opacity-30 blur transition duration-1000"></div>

                    <div className="relative bg-slate-950/90 backdrop-blur-xl rounded-2xl md:rounded-3xl border border-white/10 overflow-hidden shadow-2xl h-auto md:h-[85vh] md:min-h-[700px] flex flex-col">
                        <div className="h-1 w-full bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>

                        <div className="flex-1 relative p-0 overflow-hidden">
                            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

                            <AnimatePresence mode="wait">
                                {!sessionId ? (
                                    <motion.div
                                        key="upload"
                                        initial={{ opacity: 0, scale: 0.98 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.98 }}
                                        className="h-full flex items-center justify-center p-4 md:p-8 relative z-10"
                                    >
                                        <DocumentUpload onSessionCreated={handleSessionCreated} />
                                    </motion.div>
                                ) : (
                                    <motion.div
                                        key="chat"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="h-full flex flex-col md:flex-row relative z-10 overflow-hidden"
                                    >
                                        {/* LEFT SIDEBAR - Document Preview */}
                                        <div className={`
                                            ${showSidebar ? 'flex' : 'hidden'} 
                                            md:flex flex-col
                                            w-full md:w-[380px] lg:w-[450px] 
                                            flex-shrink-0 border-r border-white/10 bg-slate-950/50 
                                            p-4 md:p-6 gap-4 overflow-hidden
                                        `}>
                                            <div className="flex items-center justify-between">
                                                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                                    {activeDoc?.type === 'url' ? <LinkIcon size={12} className="text-cyan-400" /> : <FileText size={12} className="text-cyan-400" />}
                                                    Context
                                                </h3>
                                                <div className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 max-w-[150px] md:max-w-[200px]">
                                                    <span className="text-[10px] text-slate-300 font-mono truncate block" title={activeDoc?.name}>{activeDoc?.name}</span>
                                                </div>
                                            </div>

                                            <div className="flex-1 min-h-[300px] md:min-h-0 overflow-hidden rounded-xl border border-white/5 bg-slate-950/50 flex flex-col">
                                                {activeDoc && (
                                                    <FilePreview
                                                        content={activeDoc.content}
                                                        type={activeDoc.type}
                                                        name={activeDoc.name}
                                                    />
                                                )}
                                            </div>

                                            <div className="flex gap-2">
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={handleReset}
                                                    className="flex-1 h-10 bg-red-500/5 border-red-500/20 text-red-400/80 hover:bg-red-500 hover:text-white"
                                                >
                                                    <RefreshCcw size={14} className="mr-2" />
                                                    Reset
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => setShowSidebar(false)}
                                                    className="md:hidden h-10 text-slate-400"
                                                >
                                                    <EyeOff size={14} className="mr-2" />
                                                    Hide
                                                </Button>
                                            </div>
                                        </div>

                                        {/* RIGHT PANE - Chat Interface */}
                                        <div className="flex-1 flex flex-col min-h-0 relative">
                                            {/* Mobile Sidebar Toggle Button */}
                                            {!showSidebar && (
                                                <button
                                                    onClick={() => setShowSidebar(true)}
                                                    className="md:hidden absolute top-4 left-4 z-50 p-2 bg-primary-600/90 text-white rounded-lg shadow-lg backdrop-blur-sm border border-white/20 animate-pulse"
                                                >
                                                    <Eye size={18} />
                                                </button>
                                            )}
                                            <ChatInterface sessionId={sessionId} />
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
