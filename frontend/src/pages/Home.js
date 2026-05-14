import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="landing">
      {/* Hero */}
      <section className="hero">
        <div className="hero__badge">AI-Powered Career Tool</div>
        <h1 className="hero__title">
          Analyze. Evaluate.<br />
          <span className="accent">Get Hired.</span>
        </h1>
        <p className="hero__sub">
          Upload your resume, match it against real job descriptions,
          and get an instant AI score with actionable feedback.
        </p>
        <div className="hero__actions">
          {user ? (
            <Link to="/dashboard" className="btn btn--primary btn--lg">Go to Dashboard →</Link>
          ) : (
            <>
              <Link to="/register" className="btn btn--primary btn--lg">Get Started Free</Link>
              <Link to="/login" className="btn btn--outline btn--lg">Sign In</Link>
            </>
          )}
        </div>
      </section>

      {/* Features */}
      <section className="features">
        {FEATURES.map(f => (
          <div key={f.title} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-desc">{f.desc}</p>
          </div>
        ))}
      </section>

      {/* How it works */}
      <section className="how-it-works">
        <h2 className="section-heading">How It Works</h2>
        <div className="steps">
          {STEPS.map((s, i) => (
            <div key={i} className="step">
              <div className="step__num">{i + 1}</div>
              <h4 className="step__title">{s.title}</h4>
              <p className="step__desc">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      {!user && (
        <section className="cta">
          <h2>Ready to level up your career?</h2>
          <p>Join today and get AI-powered resume feedback in seconds.</p>
          <Link to="/register" className="btn btn--primary btn--lg">
            Create Free Account →
          </Link>
        </section>
      )}
    </div>
  );
}

const FEATURES = [
  {
    icon: "🔍",
    title: "Resume Parsing",
    desc: "Automatic text extraction from PDF and DOCX files with skill detection.",
  },
  {
    icon: "⚡",
    title: "Weighted Scoring",
    desc: "Skills match (45%), experience relevance (30%), and keyword coverage (25%).",
  },
  {
    icon: "🤖",
    title: "AI Feedback",
    desc: "Gemini-powered suggestions tailored to the specific job you're targeting.",
  },
  {
    icon: "📊",
    title: "Hire / Improve / Reject",
    desc: "Clear recommendations based on a 0–100 score against configurable thresholds.",
  },
  {
    icon: "⚙",
    title: "Async Processing",
    desc: "Background workers handle parsing and evaluation — no waiting on page.",
  },
  {
    icon: "💼",
    title: "Job Management",
    desc: "Create and manage job postings. Evaluate any resume against any role instantly.",
  },
];

const STEPS = [
  { title: "Upload Resume",      desc: "Drop a PDF or DOCX. We parse and extract skills in the background." },
  { title: "Pick a Job",         desc: "Browse or create a job posting with a full description." },
  { title: "Run Evaluation",     desc: "Our scoring engine compares your resume against the job." },
  { title: "Get Hired",          desc: "Follow the AI feedback to close the gap and land the role." },
];
