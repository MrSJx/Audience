import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Play, Image as ImageIcon, History, BarChart3, UploadCloud, AlertCircle, FileText, CheckCircle2, Loader2, Video } from "lucide-react";

import "./styles.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const initialForm = {
  platform: "instagram_reels",
  caption: "",
  durationSeconds: "",
};

const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.12
    }
  }
};

function ScoreBar({ label, value }) {
  const tone = value >= 70 ? "strong" : value >= 45 ? "mixed" : "weak";

  return (
    <div className="score-row">
      <div className="score-copy">
        <span>{label}</span>
        <strong>
          {value}/100 <em className={`tone-${tone}`}>{tone}</em>
        </strong>
      </div>
      <div className="score-track">
        <motion.div 
          className="score-fill" 
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1], delay: 0.1 }}
        />
      </div>
    </div>
  );
}

function ReportCard({ result }) {
  if (!result) {
    return (
      <motion.section 
        className="panel report-panel empty-state"
        variants={fadeInUp}
        initial="initial"
        animate="animate"
      >
        <BarChart3 size={48} strokeWidth={1.5} className="empty-state-icon" />
        <h2>Your report will appear here</h2>
        <p>
          Upload one image or short video for Instagram Reels and the backend
          will return a structured audience reaction report generated with local
          Llama 3.2 guidance.
        </p>
      </motion.section>
    );
  }

  const { report, analysis, id } = result;

  return (
    <motion.section 
      className="panel report-panel"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="panel-header">
        <div>
          <span className="eyebrow"><CheckCircle2 size={14} /> Analysis Complete</span>
          <h2>{analysis.filename}</h2>
        </div>
        <span className="report-id">#{id.slice(0, 8)}</span>
      </div>

      <p className="summary">{report.content_summary}</p>

      <div className="confidence-note">
        <AlertCircle size={20} className="shrink-0" style={{ flexShrink: 0 }} />
        <span>These scores are heuristic estimates based on the uploaded media, not a guarantee of real-world performance.</span>
      </div>

      <div className="score-grid">
        <ScoreBar label="Hook Rating" value={report.hook_score} />
        <ScoreBar label="Engagement Score" value={report.engagement_score} />
        <ScoreBar label="Boring Rate" value={report.boring_rate} />
      </div>

      <div className="two-column">
        <div className="subpanel">
          <h3>Peak Moments</h3>
          <ul>
            {report.peak_moments.map((moment) => (
               <li key={`${moment.timestamp}-${moment.event}`}>
                <strong>{moment.timestamp}</strong> {moment.event}
              </li>
            ))}
          </ul>
        </div>
        <div className="subpanel">
          <h3>Simulated Comments</h3>
          <ul>
            {report.simulated_comments.map((comment) => (
              <li key={comment}>"{comment}"</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="two-column">
        <div className="subpanel">
          <h3>Suggested Improvements</h3>
          <ul>
            {report.improvements.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="subpanel">
          <h3>Signal Snapshot</h3>
          <ul>
            <li><strong>Type</strong> {analysis.media_type}</li>
            <li><strong>Pacing</strong> {analysis.pacing_hint}</li>
            <li><strong>Brightness</strong> {analysis.brightness_score}</li>
            <li><strong>Contrast</strong> {analysis.contrast_score}</li>
            <li><strong>Saturation</strong> {analysis.saturation_score}</li>
          </ul>
        </div>
      </div>

      <div className="verdict-box" style={{ marginTop: '24px' }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
          Final Verdict
        </h3>
        <p style={{ margin: 0 }}>{report.final_verdict}</p>
      </div>
    </motion.section>
  );
}

function RecentReports({ reports }) {
  return (
    <motion.section 
      className="panel recent-panel"
      variants={fadeInUp}
      initial="initial"
      whileInView="animate"
      viewport={{ once: true, margin: "-50px" }}
    >
      <div className="panel-header">
        <div className="header">
          <History className="header-icon" />
          <div>
            <span className="eyebrow" style={{background: 'var(--color-dark)', color: 'var(--color-text-stone)'}}>Persistence</span>
            <h2>Recent Reports</h2>
          </div>
        </div>
      </div>

      {reports.length === 0 ? (
        <p style={{ color: 'var(--color-text-stone)' }}>No reports saved yet.</p>
      ) : (
        <ul className="recent-list">
          {reports.map((item) => (
            <motion.li 
              key={item.id} 
              className="recent-item"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <strong>{item.filename}</strong>
                {item.media_type?.includes('video') ? <Video size={16} /> : <ImageIcon size={16} />}
              </div>
              <span style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>#{item.id.slice(0, 8)}</span>
              <span>{new Date(item.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</span>
            </motion.li>
          ))}
        </ul>
      )}
    </motion.section>
  );
}

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // 'idle', 'loading', 'success', 'error'
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/reports`)
      .then((response) => response.json())
      .then((payload) => setReports(payload.reports ?? []))
      .catch(() => setReports([]));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setError("Choose one image or short video first.");
      return;
    }

    setStatus("loading");
    setError("");

    const payload = new FormData();
    payload.append("file", file);
    payload.append("platform", form.platform);
    if (form.caption.trim()) {
      payload.append("caption", form.caption.trim());
    }
    if (form.durationSeconds.trim()) {
      payload.append("duration_seconds", form.durationSeconds.trim());
    }

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: payload,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Analysis failed.");
      }

      setResult(data);
      const listItem = {
        id: data.id,
        created_at: data.created_at,
        platform: data.report.platform,
        media_type: data.analysis.media_type,
        filename: data.analysis.filename,
      };
      setReports((current) => [listItem, ...current].slice(0, 8));
      setStatus("success");
    } catch (submitError) {
      setError(submitError.message);
      setStatus("error");
    }
  }

  return (
    <main className="workspace">
      <motion.section 
        className="hero"
        variants={staggerContainer}
        initial="initial"
        animate="animate"
      >
        <motion.div variants={fadeInUp}>
          <span className="eyebrow"><Play size={12} fill="currentColor" /> Audience MVP</span>
          <h1>Analyze your reach</h1>
        </motion.div>
        <motion.p variants={fadeInUp} className="lead">
          Upload media, simulate likely audience response for Instagram Reels,
          and refine your content before posting.
        </motion.p>
        <motion.p variants={fadeInUp} className="sublead">
          The current MVP combines media signal extraction with local Llama 3.2
          report generation.
        </motion.p>
      </motion.section>

      <section className="layout">
        <motion.form 
          className="panel form-panel" 
          onSubmit={handleSubmit}
          variants={fadeInUp}
          initial="initial"
          animate="animate"
        >
          <div className="panel-header">
            <div>
              <span className="eyebrow">Analyze</span>
              <h2>Run a new report</h2>
            </div>
          </div>

          <label className="field">
            <span>Target platform</span>
            <select
              value={form.platform}
              onChange={(event) =>
                setForm((current) => ({ ...current, platform: event.target.value }))
              }
            >
              <option value="instagram_reels">Instagram Reels</option>
            </select>
          </label>

          <label className="field">
            <span>Media file</span>
            <div style={{ position: 'relative' }}>
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,video/mp4,video/quicktime,video/webm"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                style={{ paddingLeft: '40px' }}
              />
              <UploadCloud size={18} color="var(--color-text-stone)" style={{ position: 'absolute', left: '16px', top: '16px', pointerEvents: 'none' }} />
            </div>
          </label>

          <label className="field">
            <span>Caption context</span>
            <textarea
              rows="3"
              value={form.caption}
              onChange={(event) =>
                setForm((current) => ({ ...current, caption: event.target.value }))
              }
              placeholder="Optional context about the post tone..."
            />
          </label>

          <label className="field">
            <span>Duration override (seconds)</span>
            <input
              type="number"
              min="0"
              max="90"
              step="0.1"
              value={form.durationSeconds}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  durationSeconds: event.target.value,
                }))
              }
              placeholder="Auto-detected if video"
            />
          </label>

          <motion.button 
            type="submit" 
            className="submit-button" 
            disabled={status === "loading"}
          >
            {status === "loading" ? (
              <><Loader2 size={18} className="spin" /> Analyzing...</>
            ) : (
              <><FileText size={18} /> Analyze Content</>
            )}
          </motion.button>


          <p className="form-note">
            Supported: PNG, JPEG, WEBP, MP4, MOV, WEBM. (Max 90s)
          </p>

          {error && (
            <motion.p 
              className="error-text"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
            >
              <AlertCircle size={16} /> {error}
            </motion.p>
          )}
        </motion.form>

        <ReportCard result={result} />
      </section>

      <RecentReports reports={reports} />
    </main>
  );
}
