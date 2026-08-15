import { FormEvent, useEffect, useRef, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WELCOME = "Hello. I can help you schedule a clinic appointment. Please avoid entering detailed medical information.";

type ChatResponse = { reply: string; intent: string; safe_to_continue: boolean };
type Message = { role: "assistant" | "user"; text: string };
type SpeechResult = { isFinal: boolean; 0: { transcript: string } };
type SpeechEvent = { resultIndex: number; results: ArrayLike<SpeechResult> };
type SpeechErrorEvent = { error: string };
type Recognition = {
  continuous: boolean; interimResults: boolean; lang: string;
  start: () => void; stop: () => void;
  onstart: (() => void) | null; onend: (() => void) | null;
  onerror: ((event: SpeechErrorEvent) => void) | null;
  onresult: ((event: SpeechEvent) => void) | null;
};
type RecognitionConstructor = new () => Recognition;

export default function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", text: WELCOME }]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [voiceError, setVoiceError] = useState("");
  const recognition = useRef<Recognition | null>(null);
  const keepListening = useRef(false);
  const finalTranscript = useRef("");
  const latestTranscript = useRef("");
  const chatEnd = useRef<HTMLDivElement | null>(null);

  const speechWindow = window as typeof window & {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  };
  const speechSupported = Boolean(speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition);

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);
  useEffect(() => () => {
    keepListening.current = false;
    recognition.current?.stop();
    window.speechSynthesis?.cancel();
  }, []);

  function speak(text: string) {
    if (!voiceEnabled || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.96;
    utterance.volume = 1;
    window.setTimeout(() => window.speechSynthesis.speak(utterance), 350);
  }

  async function sendMessage(text: string) {
    const clean = text.trim();
    if (!clean || loading) return;
    setMessages((current) => [...current, { role: "user", text: clean }]);
    setMessage("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: clean }),
      });
      if (!response.ok) throw new Error("Request failed");
      const data: ChatResponse = await response.json();
      setMessages((current) => [...current, { role: "assistant", text: data.reply }]);
      speak(data.reply);
    } catch {
      setMessages((current) => [...current, { role: "assistant", text: "The service is temporarily unavailable. Please try again." }]);
    } finally { setLoading(false); }
  }

  function beginRecognition() {
    const SpeechRecognition = speechWindow.SpeechRecognition || speechWindow.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const next = new SpeechRecognition();
    next.continuous = true;
    next.interimResults = true;
    next.lang = "en-US";
    next.onstart = () => { setListening(true); setVoiceError(""); };
    next.onresult = (event) => {
      let interim = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const text = event.results[index][0]?.transcript || "";
        if (event.results[index].isFinal) finalTranscript.current += `${text} `;
        else interim += text;
      }
      latestTranscript.current = `${finalTranscript.current}${interim}`.trim();
      setMessage(latestTranscript.current);
    };
    next.onerror = (event) => {
      if (["not-allowed", "service-not-allowed", "audio-capture"].includes(event.error)) {
        keepListening.current = false;
        setListening(false);
        setVoiceError("Microphone access is unavailable. Check Edge site permissions and try again.");
      }
    };
    next.onend = () => {
      if (keepListening.current) {
        window.setTimeout(() => {
          try { next.start(); } catch { /* Edge may still be closing the previous session. */ }
        }, 200);
        return;
      }
      setListening(false);
      const complete = latestTranscript.current.trim();
      if (complete) window.setTimeout(() => void sendMessage(complete), 200);
      else setVoiceError("No speech was detected. Click Talk and try again.");
    };
    recognition.current = next;
    next.start();
  }

  function toggleListening() {
    if (!speechSupported || loading) return;
    if (listening) {
      keepListening.current = false;
      recognition.current?.stop();
      return;
    }
    window.speechSynthesis?.cancel();
    finalTranscript.current = "";
    latestTranscript.current = "";
    setMessage("");
    setVoiceError("");
    keepListening.current = true;
    beginRecognition();
  }

  function submit(event: FormEvent) { event.preventDefault(); void sendMessage(message); }

  return <main className="shell">
    <section className="hero"><div><span className="badge">PORTFOLIO PROJECT</span><h1>Healthcare AI<br />Voice Agent</h1><p>A safe-by-design voice assistant demonstrating full-stack engineering, AI orchestration and appointment scheduling.</p></div><div className="statusCard"><strong>System</strong><span>FastAPI • React • Browser Voice • AI</span><div className="online"><i /> Live demo ready</div></div></section>
    <section className="chatCard">
      <header className="chatHeader"><div><strong>Appointment Assistant</strong><span>{listening ? "Listening… press Stop when finished" : loading ? "Thinking…" : "Ready to help"}</span></div><button className="soundButton" type="button" onClick={() => { window.speechSynthesis?.cancel(); setVoiceEnabled((value) => !value); }}>{voiceEnabled ? "🔊 Voice on" : "🔇 Voice off"}</button></header>
      <div className="conversation">{messages.map((item, index) => <div className={`message ${item.role}`} key={`${item.role}-${index}`}><span>{item.role === "assistant" ? "CareVoice AI" : "You"}</span><p>{item.text}</p></div>)}{loading && <div className="message assistant"><span>CareVoice AI</span><p className="typing">•••</p></div>}<div ref={chatEnd} /></div>
      <div className="suggestions"><button type="button" onClick={() => void sendMessage("I would like to schedule an appointment next week.")}>Schedule appointment</button><button type="button" onClick={() => void sendMessage("What can you help me with?")}>What can you do?</button></div>
      <form onSubmit={submit}><button className={`micButton ${listening ? "listening" : ""}`} type="button" onClick={toggleListening} disabled={!speechSupported || loading}>{listening ? "■" : "🎙"}<span>{listening ? "Stop" : "Talk"}</span></button><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Type a message or press Talk…" aria-label="Message" /><button className="sendButton" disabled={loading || !message.trim()}>{loading ? "Sending…" : "Send"}</button></form>
      {voiceError && <div className="browserNote">{voiceError}</div>}
      {!speechSupported && <div className="browserNote">Voice input requires Microsoft Edge or a compatible browser.</div>}
      <small>AI-generated voice. This demonstration does not provide medical advice. For emergencies, contact local emergency services.</small>
    </section>
  </main>;
}
