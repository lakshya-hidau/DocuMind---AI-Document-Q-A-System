import React, { useState } from 'react';
import { Upload, Link, FileText, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

interface DocumentUploadProps {
    onSessionCreated: (sessionId: string, name: string, type: 'file' | 'url' | 'text', content: File | string) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onSessionCreated }) => {
    const [inputType, setInputType] = useState<'file' | 'url' | 'text'>('file');
    const [dragActive, setDragActive] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>('');
    const [url, setUrl] = useState<string>('');
    const [text, setText] = useState<string>('');

    const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = async (file: File) => {
        setLoading(true);
        setError('');
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post('http://localhost:8000/process/file', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            onSessionCreated(response.data.session_id, file.name, 'file', file);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to upload file");
        } finally {
            setLoading(false);
        }
    };

    const handleUrlSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url) return;
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('http://localhost:8000/process/url', { url });
            onSessionCreated(response.data.session_id, url, 'url', url);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to process URL");
        } finally {
            setLoading(false);
        }
    };

    const handleTextSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!text) return;
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('http://localhost:8000/process/text', { text });
            onSessionCreated(response.data.session_id, 'Raw Text Input', 'text', text);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to process text");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6 animate-fade-in-up">
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-md">RAG Q&A Assistant</h1>
                <p className="text-slate-200/80">Upload documents or links to start chatting with your data</p>
            </div>

            <div className="bg-white/10 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-white/20">
                <div className="flex border-b border-white/10">
                    <button
                        onClick={() => setInputType('file')}
                        className={`flex-1 py-4 text-sm font-medium transition-colors ${inputType === 'file' ? 'bg-primary-500/20 text-primary-100 border-b-2 border-primary-500' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
                    >
                        <div className="flex items-center justify-center gap-2">
                            <Upload size={18} /> File Upload
                        </div>
                    </button>
                    <button
                        onClick={() => setInputType('url')}
                        className={`flex-1 py-4 text-sm font-medium transition-colors ${inputType === 'url' ? 'bg-primary-500/20 text-primary-100 border-b-2 border-primary-500' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
                    >
                        <div className="flex items-center justify-center gap-2">
                            <Link size={18} /> URL Link
                        </div>
                    </button>
                    <button
                        onClick={() => setInputType('text')}
                        className={`flex-1 py-4 text-sm font-medium transition-colors ${inputType === 'text' ? 'bg-primary-500/20 text-primary-100 border-b-2 border-primary-500' : 'text-slate-300 hover:text-white hover:bg-white/5'}`}
                    >
                        <div className="flex items-center justify-center gap-2">
                            <FileText size={18} /> Text Input
                        </div>
                    </button>
                </div>

                <div className="p-8">
                    {error && (
                        <div className="mb-6 p-4 bg-red-900/50 border border-red-500/30 text-red-200 rounded-xl flex items-center gap-3">
                            <AlertCircle size={20} />
                            <p className="text-sm">{error}</p>
                        </div>
                    )}

                    {inputType === 'file' && (
                        <div
                            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${dragActive ? 'border-primary-500 bg-primary-500/10' : 'border-slate-500/50 hover:border-primary-400 hover:bg-white/5'}`}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                onChange={handleChange}
                                accept=".pdf,.docx,.txt"
                                disabled={loading}
                            />
                            <div className="flex flex-col items-center gap-4">
                                <div className="w-16 h-16 bg-white/10 rounded-full flex items-center justify-center text-slate-300">
                                    {loading ? <Loader2 className="animate-spin text-primary-400" size={32} /> : <Upload size={32} />}
                                </div>
                                <div>
                                    <p className="text-lg font-semibold text-white">Click to upload or drag and drop</p>
                                    <p className="text-sm text-slate-400 mt-1">PDF, DOCX, or TXT files</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {inputType === 'url' && (
                        <form onSubmit={handleUrlSubmit} className="flex flex-col gap-4">
                            <label className="block text-sm font-medium text-slate-200">Enter Website URL</label>
                            <div className="flex gap-2">
                                <input
                                    type="url"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://example.com/article"
                                    className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-slate-600 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all placeholder:text-slate-500"
                                    required
                                />
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                >
                                    {loading ? <Loader2 className="animate-spin" size={20} /> : 'Process'}
                                </button>
                            </div>
                        </form>
                    )}

                    {inputType === 'text' && (
                        <form onSubmit={handleTextSubmit} className="flex flex-col gap-4">
                            <label className="block text-sm font-medium text-slate-200">Enter Text Content</label>
                            <textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                placeholder="Paste your text here..."
                                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-slate-600 text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all min-h-[200px] placeholder:text-slate-500"
                                required
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {loading ? <Loader2 className="animate-spin" size={20} /> : 'Process Text'}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentUpload;
