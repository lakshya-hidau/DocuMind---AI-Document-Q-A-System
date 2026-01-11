import React, { useLayoutEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import MessageBubble from "./MessageBubble";

interface ChatInterfaceProps {
    sessionId: string;
}

interface Message {
    id: string;
    text: string;
    isUser: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ sessionId }) => {
    /* -------------------- STATE -------------------- */
    const [messages, setMessages] = useState<Message[]>([
        {
            id: crypto.randomUUID(),
            text: "Hello! I've processed your data. What would you like to know?",
            isUser: false,
        },
    ]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    /* -------------------- SCROLL REFS -------------------- */
    const scrollContainerRef = useRef<HTMLDivElement | null>(null);
    const isNearBottomRef = useRef(true);

    /* -------------------- SCROLL HELPERS -------------------- */
    const scrollToBottom = (smooth = true) => {
        if (!scrollContainerRef.current) return;
        const el = scrollContainerRef.current;
        el.scrollTo({
            top: el.scrollHeight,
            behavior: smooth ? "smooth" : "auto",
        });
    };

    const handleScroll = () => {
        if (!scrollContainerRef.current) return;
        const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
        isNearBottomRef.current = distanceFromBottom < 100;
    };

    /* -------------------- AUTO SCROLL LOGIC -------------------- */
    useLayoutEffect(() => {
        const last = messages[messages.length - 1];
        if (last?.isUser) {
            scrollToBottom();
            return;
        }
        if (isNearBottomRef.current) {
            scrollToBottom();
        }
    }, [messages, loading]);

    /* -------------------- SUBMIT -------------------- */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userText = input.trim();
        const userMsgId = crypto.randomUUID();
        const aiMsgId = crypto.randomUUID();

        setInput("");
        setLoading(true);
        isNearBottomRef.current = true;

        // Add user message
        setMessages((prev) => [
            ...prev,
            {
                id: userMsgId,
                text: userText,
                isUser: true,
            },
        ]);

        // Add placeholder AI message
        setMessages((prev) => [
            ...prev,
            {
                id: aiMsgId,
                text: "",
                isUser: false,
            },
        ]);

        try {
            const response = await fetch("http://localhost:8000/chat/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    query: userText,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || "Failed to get response");
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) throw new Error("Response body is null");

            let accumulatedText = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                accumulatedText += chunk;

                // Update the placeholder AI message with accumulated text
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === aiMsgId ? { ...msg, text: accumulatedText } : msg
                    )
                );
            }
        } catch (err: any) {
            console.error("Chat request error:", err);
            const serverMessage = err?.message || "Something went wrong";
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === aiMsgId ? { ...msg, text: `⚠️ ${serverMessage}` } : msg
                )
            );
        } finally {
            setLoading(false);
        }
    };

    /* -------------------- UI -------------------- */
    return (
        <div className="flex flex-col h-full bg-slate-950/40 text-white overflow-hidden" style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}>
            {/* CHAT MESSAGES AREA */}
            <div
                ref={scrollContainerRef}
                onScroll={handleScroll}
                className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6 custom-scrollbar"
            >
                <div className="max-w-4xl mx-auto w-full space-y-6">
                    {messages.map((msg) => (
                        msg.text || msg.isUser ? (
                            <MessageBubble
                                key={msg.id}
                                message={msg.text}
                                isUser={msg.isUser}
                            />
                        ) : null
                    ))}

                    {loading && !messages.find(m => m.isUser === false && m.text !== "") && (
                        <div className="flex items-center gap-3 text-slate-400 pl-4 py-2">
                            <div className="flex space-x-1">
                                <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce"></div>
                            </div>
                            <span className="text-xs font-medium tracking-wider uppercase opacity-70">Processing</span>
                        </div>
                    )}
                </div>
            </div>

            {/* INPUT AREA */}
            <div className="p-3 md:p-6 bg-gradient-to-t from-slate-950 via-slate-950 to-transparent">
                <form
                    onSubmit={handleSubmit}
                    className="max-w-4xl mx-auto relative group"
                >
                    <div className="absolute -inset-1 bg-gradient-to-r from-primary-500/20 to-cyan-500/20 rounded-2xl blur opacity-0 group-focus-within:opacity-100 transition duration-500"></div>
                    <div className="relative flex items-center gap-2 bg-slate-900/80 backdrop-blur-md border border-white/10 p-2 rounded-2xl shadow-xl">
                        <input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask DocuMind anything..."
                            disabled={loading}
                            className="flex-1 bg-transparent border-none px-4 py-3 text-white placeholder-slate-500 outline-none text-sm md:text-base"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || loading}
                            className="p-3 rounded-xl bg-primary-600 hover:bg-primary-500 disabled:opacity-30 disabled:hover:bg-primary-600 transition-all shadow-lg shadow-primary-900/20 active:scale-95"
                        >
                            <Send size={18} className={loading ? "animate-pulse" : ""} />
                        </button>
                    </div>
                    <p className="text-[10px] text-slate-500 text-center mt-3 uppercase tracking-widest font-medium opacity-50">
                        DocuMind can make mistakes. Verify important information.
                    </p>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
