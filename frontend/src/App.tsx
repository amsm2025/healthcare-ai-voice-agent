import { FormEvent, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

type ChatResponse = {
  reply: string;
  intent: string;
  safe_to_continue: boolean;
};

export default function App() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState(
    "Hello. I can help you schedule a clinic appointment. Please avoid entering detailed medical information."
  );
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const data: ChatResponse = await response.json();
      setReply(data.reply);
      setMessage("");
    } catch {
      setReply("The service is temporarily unavailable. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div>
          <span className="badge">PORTFOLIO PROJECT</span>
          <h1>Healthcare AI<br />Voice Agent</h1>
          <p>
            A safe-by-design appointment assistant demonstrating full-stack
            engineering, AI orchestration and scheduling integration.
          </p>
        </div>
        <div className="statusCard">
          <strong>System</strong>
          <span>FastAPI • React • AI • Cal.com</span>
          <div className="online"><i /> Demo ready</div>
        </div>
      </section>

      <section className="chatCard">
        <div className="chatHeader">
          <div>
            <strong>Appointment Assistant</strong>
            <span>Non-diagnostic scheduling demo</span>
          </div>
        </div>

        <div className="response">{reply}</div>

        <form onSubmit={submit}>
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Example: I'd like to schedule an appointment next week"
          />
          <button disabled={loading}>{loading ? "Sending..." : "Send"}</button>
        </form>

        <small>
          This demo does not provide medical advice. For emergencies, contact local emergency services.
        </small>
      </section>
    </main>
  );
}
