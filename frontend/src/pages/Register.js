import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Btn, toast } from "../components/UI";

export default function Register() {
  const { register } = useAuth();
  const navigate     = useNavigate();
  const [form, setForm]     = useState({ username: "", email: "", password: "", confirm_password: "" });
  const [loading, setLoading] = useState(false);

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm_password) {
      toast.error("Passwords do not match.");
      return;
    }
    if (form.password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast.success("Account created! Please log in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.response?.data?.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-brand">
        <div className="auth-brand__icon">◈</div>
        <h1 className="auth-brand__title">ResumeAI</h1>
        <p className="auth-brand__sub">Intelligent career acceleration</p>
        <div className="auth-brand__dots">
          {[...Array(6)].map((_, i) => (
            <span key={i} className="dot" style={{ animationDelay: `${i * 0.4}s` }} />
          ))}
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-form-wrap">
          <h2 className="auth-title">Create Account</h2>
          <p className="auth-sub">Already have one? <Link to="/login">Sign in</Link></p>

          <form onSubmit={submit} className="auth-form">
            <div className="field">
              <label>Username</label>
              <input name="username" value={form.username} onChange={handle}
                placeholder="your_username" required autoComplete="username" />
            </div>
            <div className="field">
              <label>Email</label>
              <input name="email" type="email" value={form.email} onChange={handle}
                placeholder="you@example.com" required autoComplete="email" />
            </div>
            <div className="field">
              <label>Password</label>
              <input name="password" type="password" value={form.password} onChange={handle}
                placeholder="Min. 8 characters" required autoComplete="new-password" />
            </div>
            <div className="field">
              <label>Confirm Password</label>
              <input name="confirm_password" type="password" value={form.confirm_password}
                onChange={handle} placeholder="••••••••" required autoComplete="new-password" />
            </div>
            <Btn type="submit" loading={loading} style={{ width: "100%", marginTop: 8 }}>
              Create Account →
            </Btn>
          </form>
        </div>
      </div>
    </div>
  );
}