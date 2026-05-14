import { useState, useEffect } from "react";
import { jobAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { Card, Btn, toast, PageLoader } from "../components/UI";

export default function JobsPage() {
  const { user }              = useAuth();
  const [jobs, setJobs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage]       = useState(1);
  const [total, setTotal]     = useState(0);
  const [showForm, setShowForm] = useState(false);

  const fetchJobs = async (p = 1) => {
    setLoading(true);
    try {
      const r = await jobAPI.list(p);
      setJobs(r.data.items || []);
      setTotal(r.data.total || 0);
    } catch {
      toast.error("Failed to load jobs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchJobs(page); }, [page]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this job posting?")) return;
    try {
      await jobAPI.delete(id);
      toast.success("Job deleted.");
      fetchJobs(page);
    } catch {
      toast.error("Failed to delete job.");
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Job Postings</h1>
          <p className="page-sub">{total} job{total !== 1 ? "s" : ""} available</p>
        </div>
        <Btn onClick={() => setShowForm(v => !v)}>
          {showForm ? "✕ Cancel" : "+ New Job"}
        </Btn>
      </div>

      {showForm && (
        <CreateJobForm onCreated={() => { setShowForm(false); fetchJobs(1); }} />
      )}

      {loading ? (
        <PageLoader />
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💼</div>
          <p>No job postings yet. Create the first one!</p>
        </div>
      ) : (
        <div className="jobs-grid">
          {jobs.map(job => (
            <JobCard
              key={job.id}
              job={job}
              canDelete={user && job.created_by === user.user_id}
              onDelete={() => handleDelete(job.id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 20 && (
        <div className="pagination">
          <button
            className="btn btn--outline btn--sm"
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
          >← Prev</button>
          <span className="page-info">Page {page} of {Math.ceil(total / 20)}</span>
          <button
            className="btn btn--outline btn--sm"
            disabled={page * 20 >= total}
            onClick={() => setPage(p => p + 1)}
          >Next →</button>
        </div>
      )}
    </div>
  );
}

/* ── Job Card ─────────────────────────────────────────────────────────────── */
function JobCard({ job, canDelete, onDelete }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="job-card">
      <div className="job-card__header">
        <div>
          <h3 className="job-title">{job.title}</h3>
          {job.company && <p className="job-company">{job.company}</p>}
        </div>
        <div className="job-card__actions">
          <a
            href={`/evaluate?job_id=${job.id}`}
            className="btn btn--sm btn--primary"
          >
            Evaluate →
          </a>
          {canDelete && (
            <button className="btn btn--sm btn--danger" onClick={onDelete}>
              Delete
            </button>
          )}
        </div>
      </div>

      {job.required_skills?.length > 0 && (
        <div className="job-skills">
          {job.required_skills.slice(0, 6).map(s => (
            <span key={s} className="skill-tag">{s}</span>
          ))}
          {job.required_skills.length > 6 && (
            <span className="skill-tag skill-tag--more">
              +{job.required_skills.length - 6} more
            </span>
          )}
        </div>
      )}

      <p className={`job-desc${expanded ? " job-desc--expanded" : ""}`}>
        {job.description}
      </p>
      {job.description?.length > 160 && (
        <button
          className="expand-btn"
          onClick={() => setExpanded(v => !v)}
        >
          {expanded ? "Show less ↑" : "Show more ↓"}
        </button>
      )}

      <div className="job-meta">
        <span className="meta-muted">ID #{job.id}</span>
        <span className="meta-muted">{fmtDate(job.created_at)}</span>
      </div>
    </Card>
  );
}

/* ── Create Job Form ─────────────────────────────────────────────────────── */
function CreateJobForm({ onCreated }) {
  const [form, setForm]       = useState({ title: "", company: "", description: "" });
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    if (form.description.trim().split(/\s+/).length < 15) {
      toast.error("Job description must be at least 15 words.");
      return;
    }
    setLoading(true);
    try {
      await jobAPI.create(form);
      toast.success("Job posting created!");
      onCreated();
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to create job.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="create-form">
      <h3 className="card-title">New Job Posting</h3>
      <form onSubmit={submit}>
        <div className="form-row">
          <div className="field">
            <label>Job Title *</label>
            <input name="title" value={form.title} onChange={handle}
              placeholder="e.g. Senior Backend Engineer" required />
          </div>
          <div className="field">
            <label>Company</label>
            <input name="company" value={form.company} onChange={handle}
              placeholder="e.g. Acme Corp" />
          </div>
        </div>
        <div className="field">
          <label>Job Description * <span className="field-hint">(min 15 words)</span></label>
          <textarea
            name="description"
            value={form.description}
            onChange={handle}
            placeholder="Describe the role, requirements, responsibilities..."
            rows={6}
            required
          />
        </div>
        <div className="form-actions">
          <Btn type="submit" loading={loading}>Create Job Posting</Btn>
        </div>
      </form>
    </Card>
  );
}

function fmtDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric"
  });
}