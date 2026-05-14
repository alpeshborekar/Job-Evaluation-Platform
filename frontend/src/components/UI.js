import { useEffect, useState } from "react";

import {
  Link,
  useNavigate,
  useLocation,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Nav() {
  const { user, logout } = useAuth();

  const navigate = useNavigate();

  const loc = useLocation();

  const [scrolled, setScrolled] =
    useState(false);

  useEffect(() => {
    const h = () =>
      setScrolled(window.scrollY > 10);

    window.addEventListener("scroll", h);

    return () =>
      window.removeEventListener("scroll", h);
  }, []);

  const handleLogout = async () => {
    await logout();

    navigate("/login");
  };

  const active = (path) =>
    loc.pathname === path
      ? "nav-link active"
      : "nav-link";

  return (
    <nav
      className={`nav${
        scrolled ? " nav--scrolled" : ""
      }`}
    >
      <Link to="/" className="nav-logo">
        <span className="logo-icon">
          ◈
        </span>

        {" "}ResumeAI
      </Link>

      {user && (
        <div className="nav-links">
          <Link
            to="/dashboard"
            className={active(
              "/dashboard",
            )}
          >
            Dashboard
          </Link>

          <Link
            to="/resume"
            className={active("/resume")}
          >
            Upload
          </Link>

          <Link
            to="/jobs"
            className={active("/jobs")}
          >
            Jobs
          </Link>

          <Link
            to="/evaluate"
            className={active(
              "/evaluate",
            )}
          >
            Evaluate
          </Link>

          <button
            onClick={handleLogout}
            className="nav-btn-outline"
          >
            Logout
          </button>
        </div>
      )}

      {!user && (
        <div className="nav-links">
          <Link
            to="/login"
            className={active("/login")}
          >
            Login
          </Link>

          <Link
            to="/register"
            className="nav-btn"
          >
            Get Started
          </Link>
        </div>
      )}
    </nav>
  );
}

export function ProtectedRoute({
  children,
}) {
  const { user, loading } = useAuth();

  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login");
    }
  }, [user, loading, navigate]);

  if (loading) {
    return <PageLoader />;
  }

  return user ? children : null;
}

export function PageLoader() {
  return (
    <div className="page-loader">
      <div className="spinner" />
    </div>
  );
}

let _setToast = null;

export function ToastProvider() {
  const [toast, setToast] =
    useState(null);

  _setToast = setToast;

  useEffect(() => {
    if (!toast) return;

    const t = setTimeout(
      () => setToast(null),
      3500,
    );

    return () => clearTimeout(t);
  }, [toast]);

  if (!toast) return null;

  return (
    <div
      className={`toast toast--${toast.type}`}
    >
      {toast.type === "success"
        ? "✓"
        : "✕"}{" "}

      {toast.msg}
    </div>
  );
}

export const toast = {
  success: (msg) =>
    _setToast?.({
      type: "success",
      msg,
    }),

  error: (msg) =>
    _setToast?.({
      type: "error",
      msg,
    }),
};

export function ScoreRing({
  score = 0,
  size = 120,
}) {
  const r = 44;

  const circ = 2 * Math.PI * r;

  const fill = (
    (score / 100) * circ
  ).toFixed(2);

  const color =
    score >= 75
      ? "#00d4ff"
      : score >= 45
      ? "#f0a500"
      : "#ff5a5a";

  return (
    <div
      className="score-ring"
      style={{
        width: size,
        height: size,
      }}
    >
      <svg
        viewBox="0 0 100 100"
        width={size}
        height={size}
      >
        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="8"
        />

        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${fill} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{
            transition:
              "stroke-dasharray 1s ease",
          }}
        />
      </svg>

      <span
        className="score-ring__num"
        style={{ color }}
      >
        {score}
      </span>
    </div>
  );
}

export function Badge({
  label,
  variant = "match",
}) {
  return (
    <span
      className={`badge badge--${variant}`}
    >
      {label}
    </span>
  );
}

export function StatusChip({
  status,
}) {
  const map = {
    pending: [
      "chip--pending",
      "⏳ Pending",
    ],

    processing: [
      "chip--processing",
      "⚙ Processing",
    ],

    completed: [
      "chip--done",
      "✓ Done",
    ],

    failed: [
      "chip--fail",
      "✕ Failed",
    ],
  };

  const [cls, label] =
    map[status] || [
      "chip--pending",
      status,
    ];

  return (
    <span className={`chip ${cls}`}>
      {label}
    </span>
  );
}

export function Card({
  children,
  className = "",
}) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}

export function Btn({
  children,
  variant = "primary",
  loading,
  ...props
}) {
  return (
    <button
      className={`btn btn--${variant}`}
      disabled={loading}
      {...props}
    >
      {loading
        ? <span className="btn-spinner" />
        : children}
    </button>
  );
}