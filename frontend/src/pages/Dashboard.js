import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { resumeAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { Card, StatusChip, PageLoader } from "../components/UI";

export default function Dashboard() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    resumeAPI.list(1)
      .then(r => setResumes(r.data.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageLoader />;

  const completed   = resumes.filter(r => r.parse_status === "completed").length;
  const avgSkills   = resumes.length
    ? Math.round(resumes.reduce((a, r) => a + (r.skills_found?.length || 0), 0) / resumes.length)
    : 0;

  return (
    <div className="page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Hey, <span className="accent">{user?.username}</span> 👋
          </h1>
          <p className="page-sub">Here's your activity overview.</p>
        </div>
        <div className="header-actions">
          <Link to="/resume" className="btn btn--primary">+ Upload Resume</Link>
          <Link to="/evaluate" className="btn btn--outline">Run Evaluation</Link>
        </div>
      </div>

      {/* Stat cards */}
      <div className="stat-grid">
        <Card className="stat-card">
          <div className="stat-label">Total Resumes</div>
          <div className="stat-num">{resumes.length}</div>
          <div className="stat-hint">uploaded</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-label">Parsed</div>
          <div className="stat-num">{completed}</div>
          <div className="stat-hint">ready to evaluate</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-label">Avg. Skills Found</div>
          <div className="stat-num">{avgSkills}</div>
          <div className="stat-hint">per resume</div>
        </Card>
        <Card className="stat-card">
          <div className="stat-label">Quick Links</div>
          <div className="quick-links">
            <Link to="/jobs">Browse Jobs</Link>
            <Link to="/evaluate">Evaluate</Link>
          </div>
        </Card>
      </div>

      {/* Recent resumes */}
      <section className="section">
        <div className="section-head">
          <h2 className="section-title">Recent Resumes</h2>
          <Link to="/resume" className="section-link">View all →</Link>
        </div>

        {resumes.length === 0 ? (
          <EmptyState
            icon="📄"
            text="No resumes yet."
            action={{ label: "Upload your first", to: "/resume" }}
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Type</th>
                  <th>Skills Found</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {resumes.slice(0, 6).map(r => (
                  <tr key={r.id}>
                    <td className="td-name">{r.original_name}</td>
                    <td><span className="tag">{r.file_type?.toUpperCase()}</span></td>
                    <td>{r.skills_found?.length || 0}</td>
                    <td><StatusChip status={r.parse_status} /></td>
                    <td className="td-muted">{fmtDate(r.uploaded_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function EmptyState({ icon, text, action }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <p>{text}</p>
      {action && <Link to={action.to} className="btn btn--primary">{action.label}</Link>}
    </div>
  );
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}