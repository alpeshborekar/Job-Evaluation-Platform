import {
  BrowserRouter,
  Routes,
  Route,
  Outlet,
} from "react-router-dom";

import {
  AuthProvider,
} from "./context/AuthContext";

import {
  Nav,
  ProtectedRoute,
  ToastProvider,
} from "./components/UI";

import Home from "./pages/Home";

import Login from "./pages/Login";

import Register from "./pages/Register";

import Dashboard from "./pages/Dashboard";

import ResumePage from "./pages/ResumePage";

import JobsPage from "./pages/JobsPage";

import EvaluatePage from "./pages/EvaluatePage";

import ProfilePage from "./pages/ProfilePage";


function Layout() {

  return (
    <>
      <Nav />

      <main className="app-main">

        <div className="page">

          <Outlet />

        </div>

      </main>

      <ToastProvider />
    </>
  );
}


export default function App() {

  return (
    <AuthProvider>

      <BrowserRouter>

        <Routes>

          <Route
            element={<Layout />}
          >

            <Route
              path="/"
              element={<Home />}
            />

            <Route
              path="/login"
              element={<Login />}
            />

            <Route
              path="/register"
              element={<Register />}
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/resume"
              element={
                <ProtectedRoute>
                  <ResumePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/jobs"
              element={
                <ProtectedRoute>
                  <JobsPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/evaluate"
              element={
                <ProtectedRoute>
                  <EvaluatePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="*"
              element={
                <div
                  className="page"
                  style={{
                    textAlign: "center",
                    paddingTop: 80,
                  }}
                >

                  <div
                    style={{
                      fontSize: "4rem",
                      marginBottom: 16,
                    }}
                  >
                    404
                  </div>

                  <p className="muted">
                    Page not found.
                  </p>

                  <a
                    href="/"
                    className="btn btn--primary"
                    style={{
                      marginTop: 20,
                      display: "inline-flex",
                    }}
                  >
                    Go Home
                  </a>
                </div>
              }
            />

          </Route>

        </Routes>

      </BrowserRouter>

    </AuthProvider>
  );
}