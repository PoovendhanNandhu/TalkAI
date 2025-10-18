import { useEffect, useMemo, useRef, useState } from "react";

type Segment = { text: string; lang: "en" | "hi" };
type Preview = { segments: Segment[] };

const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export default function App() {
  const [text, setText] = useState<string>(
    "Namaste 🙏 welcome to our सेवा! Type Hinglish: Yeh service Hindi aur English दोनों बोलती है."
  );
  const [speed, setSpeed] = useState<number>(1.0);
  const [pause, setPause] = useState<number>(160);
  const [loading, setLoading] = useState<boolean>(false);
  const [audioUrl, setAudioUrl] = useState<string>("");
  const [segments, setSegments] = useState<Segment[]>([]);
  const audioRef = useRef<HTMLAudioElement>(null);
  const chars = text.length;
  

  // Build a cancellable preview request whenever inputs change
  const segChips = useMemo(() => {
    const controller = new AbortController();
    const run = async () => {
      try {
        const res = await fetch(`${API}/segments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, speed, pause_ms: pause }),
          signal: controller.signal,
        });
        if (!res.ok) return [];
        const data: Preview = await res.json();
        return data.segments || [];
      } catch {
        return [];
      }
    };
    return { promise: run(), cancel: () => controller.abort() };
  }, [text, speed, pause]);

  useEffect(() => {
    let mounted = true;
    segChips.promise.then((segs) => {
      if (mounted) setSegments(segs);
    });
    return () => {
      mounted = false;
      segChips.cancel();
    };
  }, [segChips]);

  const speak = async () => {
    try {
      setLoading(true);
      setAudioUrl("");
      const res = await fetch(`${API}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, speed, pause_ms: pause }),
      });
      if (!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
      setTimeout(() => audioRef.current?.play(), 100);
    } catch (e: any) {
      alert("TTS failed. Check backend & ffmpeg/libsndfile. " + (e?.message || ""));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="card">
        <h1>Hinglish Text-to-Speech</h1>
        <p className="badge">Mixed Hindi + English supported</p>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type Hinglish here..."
        />
        <div className="controls">
          <div className="group small">
            <label>Speed: {speed.toFixed(2)}×</label>
            <input
              type="range"
              min={0.7}
              max={1.4}
              step={0.01}
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
            />
          </div>
          <div className="group small">
            <label>Pause between segments: {pause} ms</label>
            <input
              type="range"
              min={0}
              max={600}
              step={20}
              value={pause}
              onChange={(e) => setPause(parseInt(e.target.value))}
            />
          </div>
          <div className="group small">
            <label>Characters</label>
            <div className="badge">{chars}</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
          <button className="primary" onClick={speak} disabled={loading || !text.trim()}>
            {loading ? "Synthesizing…" : "Speak"}
          </button>
          <button
            onClick={() => {
              setText("");
              setSegments([]);
              setAudioUrl("");
            }}
          >
            Clear
          </button>
          {audioUrl && (
            <a download="hinglish-tts.mp3" href={audioUrl}>
              <button>Download MP3</button>
            </a>
          )}
        </div>
      </div>

      <div className="card">
        <strong>Detected Segments</strong>
        <div className="segments" style={{ marginTop: 8 }}>
          {segments.length === 0 && <span className="badge">No segments yet (type above)</span>}
          {segments.map((s, i) => (
            <span key={i} className={`chip ${s.lang}`}>
              {s.lang.toUpperCase()}: “{s.text}”
            </span>
          ))}
        </div>
      </div>

      <div className="card">
        <audio ref={audioRef} className="audio" controls src={audioUrl || undefined} />
      </div>
    </div>
  );
}
