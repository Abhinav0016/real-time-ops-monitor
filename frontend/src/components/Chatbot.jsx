import React, { useEffect, useState, useRef } from 'react';
import { MessageSquare, Send, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const SUGGESTED_QUESTIONS = {
    "Fleet Operations Manager": [
        "Which region is underperforming?",
        "What is the total revenue impact today?",
        "Are we exceeding data usage limits?",
        "Where should I allocate resources?"
    ],
    "NOC Analyst": [
        "How many towers are down?",
        "What is the root cause of the current latency?",
        "Which devices have recurring failures?",
        "Show me critical alerts for Site C."
    ],
    "Site Supervisor": [
        "Which sites need maintenance today?",
        "Where should I allocate resources?",
        "Are there any physical site issues reported?",
        "Check battery levels for high-load sites."
    ]
};

export default function OperationalChat({ userRole }) {
    const [isOpen, setIsOpen] = useState(false);
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([
        { role: 'ai', content: `Hello! I'm your AI Operational Assistant for the ${userRole} role. How can I help you today?` }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [chatHistory]);

    const sendMessage = async (content) => {
        if (!content.trim()) return;

        const userMessage = { role: 'user', content };
        setChatHistory(prev => [...prev, userMessage]);
        setMessage('');
        setIsTyping(true);

        try {
            const response = await fetch('http://localhost:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: content, role: userRole })
            });
            const data = await response.json();
            setChatHistory(prev => [...prev, { role: 'ai', content: data.response }]);
        } catch (error) {
            setChatHistory(prev => [...prev, { role: 'ai', content: "Sorry, I'm having trouble connecting to the network intelligence layer." }]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        sendMessage(message);
    };

    const suggestions = SUGGESTED_QUESTIONS[userRole] || [];

    return (
        <div className={`operational-chat-widget ${isOpen ? 'open' : ''}`}>
            {!isOpen ? (
                <button className="chat-toggle-btn pulse-blue" onClick={() => setIsOpen(true)}>
                    <MessageSquare size={24} />
                    <span>Ask AI Assistant</span>
                </button>
            ) : (
                <div className="chat-window glass-panel shadow-2xl">
                    <div className="chat-header">
                        <div className="header-info">
                            <MessageSquare size={18} className="text-blue-400" />
                            <div className="header-content">
                                <h3>Operational AI</h3>
                                <span className="role-tag">{userRole}</span>
                            </div>
                        </div>
                        <button className="close-btn" onClick={() => setIsOpen(false)}>
                            <X size={18} />
                        </button>
                    </div>

                    <div className="chat-messages" ref={scrollRef}>
                        {chatHistory.map((msg, i) => (
                            <div key={i} className={`message-bubble ${msg.role}`}>
                                <div className="message-content">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        ))}
                        {chatHistory.length === 1 && !isTyping && (
                            <div className="suggestions-container fade-in">
                                <p className="suggestions-title">Typical questions for your role:</p>
                                <div className="suggestions-grid">
                                    {suggestions.map((q, i) => (
                                        <button key={i} className="suggestion-chip" onClick={() => sendMessage(q)}>
                                            {q}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {isTyping && (
                            <div className="message-bubble ai typing">
                                <div className="typing-indicator">
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        )}
                    </div>

                    <form className="chat-input-form" onSubmit={handleFormSubmit}>
                        <input
                            type="text"
                            placeholder="Ask about root cause, actions..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            autoFocus
                        />
                        <button type="submit" disabled={!message.trim() || isTyping}>
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
