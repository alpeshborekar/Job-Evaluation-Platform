import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { authAPI } from "../api/client";
import { Card, Btn, toast } from "../components/UI";

export default function ProfilePage() {
  const { user, logout }      = useAuth();
  const [form, setForm]       = useState({ old_password: "", new_password: "", confirm: "" });
  const [loading, setLoading] = useState(false);
  const [section, setSection] = useState("account");

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const changePassword = async (e) => {
    e.preventDefault();
    if (form.new_password !== form.confirm) {
      toast.error("New passwords do not match.");
      return;
    }
    if (form.new_password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await authAPI.changePassword({
        old_password: form.old_password,
        new_password: form.new_password,
      });
      toast.success("Password updated successfully.");
      setForm({ old_password: "", new_password: "", confirm: "" });
    } catch (err) {
      toast.error(err.response?.data?.message || "Failed to update password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page page--narrow">
      <h1 className="page-title">Profile & Settings</h1>

      {/* Tab nav */}
      <div className="tab-nav">
        {["account", "security"].map(t => (
          <button
            key={t}
            className={`tab-btn${section === t ? " tab-btn--active" : ""}`}
            onClick={() => setSection(t)}
          >
            {t === "account" ? "Account Info" : "Security"}
          </button>
        ))}
      </div>

      {section === "account" && (
        <Card>
          <h3 className="card-title">Account Information</h3>
          <div className="profile-info">
            <div className="profile-avatar">
              {user?.username?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="profile-details">
              <div className="meta-row">
                <span className="meta-label">Username</span>
                <span className="mono">{user?.username}</span>
              </div>
              <div className="meta-row">
                <span className="meta-label">User ID</span>
                <span className="mono">#{user?.user_id}</span>
              </div>
            </div>
          </div>
          <div className="danger-zone">
            <h4 className="danger-zone__title">Danger Zone</h4>
            <p className="muted" style={{ marginBottom: 12 }}>
              Logging out will end your current session.
            </p>
            <Btn variant="danger" onClick={logout}>Log Out</Btn>
          </div>
        </Card>
      )}

      {section === "security" && (
        <Card>
          <h3 className="card-title">Change Password</h3>
          <form onSubmit={changePassword} className="auth-form">
            <div className="field">
              <label>Current Password</label>
              <input
                name="old_password" type="password"
                value={form.old_password} onChange={handle}
                placeholder="••••••••" required
              />
            </div>
            <div className="field">
              <label>New Password</label>
              <input
                name="new_password" type="password"
                value={form.new_password} onChange={handle}
                placeholder="Min. 8 characters" required
              />
            </div>
            <div className="field">
              <label>Confirm New Password</label>
              <input
                name="confirm" type="password"
                value={form.confirm} onChange={handle}
                placeholder="••••••••" required
              />
            </div>
            <Btn type="submit" loading={loading} style={{ marginTop: 8 }}>
              Update Password
            </Btn>
          </form>
        </Card>
      )}
    </div>
  );
}
