import { useState } from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import {
  Btn,
  toast,
} from "../components/UI";

export default function Login() {
  const { login } = useAuth();

  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [loading, setLoading] =
    useState(false);

  const handle = (e) =>
    setForm((f) => ({
      ...f,
      [e.target.name]: e.target.value,
    }));

  const submit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      await login(form);

      toast.success("Welcome back!");

      navigate("/dashboard");
    } catch (err) {
      toast.error(
        err.response?.data?.message ||
          "Login failed.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-brand">
        <div className="auth-brand__icon">
          ◈
        </div>

        <h1 className="auth-brand__title">
          ResumeAI
        </h1>

        <p className="auth-brand__sub">
          Intelligent career acceleration
        </p>

        <div className="auth-brand__dots">
          {[...Array(6)].map((_, i) => (
            <span
              key={i}
              className="dot"
              style={{
                animationDelay: `${
                  i * 0.4
                }s`,
              }}
            />
          ))}
        </div>
      </div>

      <div className="auth-panel">
        <div className="auth-form-wrap">
          <h2 className="auth-title">
            Sign In
          </h2>

          <p className="auth-sub">
            Don't have an account?{" "}

            <Link to="/register">
              Create one
            </Link>
          </p>

          <form
            onSubmit={submit}
            className="auth-form"
          >
            <div className="field">
              <label>
                Username
              </label>

              <input
                name="username"
                value={form.username}
                onChange={handle}
                placeholder="your_username"
                required
                autoComplete="username"
              />
            </div>

            <div className="field">
              <label>
                Password
              </label>

              <input
                name="password"
                type="password"
                value={form.password}
                onChange={handle}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>

            <Btn
              type="submit"
              loading={loading}
              style={{
                width: "100%",
                marginTop: 8,
              }}
            >
              Sign In →
            </Btn>
          </form>
        </div>
      </div>
    </div>
  );
}