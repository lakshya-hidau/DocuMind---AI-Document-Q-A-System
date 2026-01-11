import React from 'react';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
    message: string;
    isUser: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isUser }) => {
    return (
        <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
                <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${isUser ? 'bg-gradient-to-br from-primary-600 to-primary-700 shadow-lg shadow-primary-500/30' : 'bg-slate-800 border border-white/20 shadow-md'}`}>
                    {isUser ? <User size={18} className="text-white" /> : <Bot size={18} className="text-primary-400" />}
                </div>
                <div className={`flex flex-col w-full leading-relaxed p-4 ${isUser ? 'bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl rounded-br-md text-white shadow-lg shadow-primary-500/20' : 'bg-slate-800/90 border border-white/10 rounded-2xl rounded-bl-md text-slate-100 shadow-lg backdrop-blur-sm'}`}>
                    <p className="text-[15px] font-normal whitespace-pre-wrap">{message}</p>
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
