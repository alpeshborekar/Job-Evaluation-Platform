import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { evaluationAPI, resumeAPI, jobAPI } from "../api/client";
import { usePolling } from "../hooks/usePolling";
import {
  Btn,
  Card,
  ScoreRing,
  Badge,
  StatusChip,
  PageLoader,
  toast,
} from "../components/UI";

export default function EvaluatePage() {
  const [searchParams] = useSearchParams();

  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);

  const [resumeId, setResumeId] = useState(
    searchParams.get("resume_id") || ""
  );

  const [jobId, setJobId] = useState(
    searchParams.get("job_id") || ""
  );

  const [submitting, setSubmitting] = useState(false);

  const [taskId, setTaskId] = useState(null);

  const [evalId, setEvalId] = useState(null);

  const [result, setResult] = useState(null);

  const [loadingInit, setLoadingInit] = useState(true);

  useEffect(() => {
    Promise.all([
      resumeAPI.list(1),
      jobAPI.list(1),
    ])
      .then(([rRes, jRes]) => {

        setResumes(
          rRes.data.items?.filter(
            (r) =>
              r.parse_status === "completed"
          ) || []
        );

        setJobs(
          jRes.data.items || []
        );
      })
      .catch(() => {
        toast.error(
          "Failed to load data."
        );
      })
      .finally(() => {
        setLoadingInit(false);
      });
  }, []);

  // Submit evaluation
  const submit = async () => {

    if (!resumeId || !jobId) {
      toast.error(
        "Select both a resume and a job."
      );
      return;
    }

    setSubmitting(true);

    try {

      const r = await evaluationAPI.submit({
        resume_id: parseInt(resumeId),
        job_id: parseInt(jobId),
      });

      // Cached completed result
      if (
        typeof r.data.total_score === "number"
      ) {
        setResult(r.data);
        return;
      }

      // Background processing
      setTaskId(r.data.task_id);

      setEvalId(
        r.data.evaluation_id
      );

      toast.success(
        "Evaluation queued…"
      );

    } catch (err) {

      toast.error(
        err.response?.data?.message ||
        "Submission failed."
      );

    } finally {

      setSubmitting(false);

    }
  };

  // Polling
  const {
    data: pollData,
    done,
  } = usePolling(
    () =>
      evaluationAPI.pollTask(taskId),
    {
      enabled: !!taskId,
      interval: 2500,
    }
  );

  // Fetch final evaluation
  useEffect(() => {

    if (done && evalId) {

      evaluationAPI
        .get(evalId)
        .then((r) => {

          console.log(
            "FINAL EVALUATION:",
            r.data
          );

          setResult(r.data);

        })
        .catch(() => {

          toast.error(
            "Failed to fetch result."
          );

        });
    }

  }, [done, evalId]);

  const reset = () => {

    setTaskId(null);

    setEvalId(null);

    setResult(null);

    setResumeId("");

    setJobId("");
  };

  if (loadingInit) {
    return <PageLoader />;
  }

  if (result) {
    return (
      <EvalResult
        result={result}
        onReset={reset}
      />
    );
  }

  return (
    <div className="page page--narrow">

      <h1 className="page-title">
        Candidate Evaluation
      </h1>

      <p className="page-sub">
        Match a resume against a job
        description to get an
        AI-powered score and
        recommendation.
      </p>

      <Card>

        {/* Resume */}
        <div className="field">

          <label>
            Select Resume{" "}
            <span className="field-hint">
              (parsed only)
            </span>
          </label>

          <select
            value={resumeId}
            onChange={(e) =>
              setResumeId(
                e.target.value
              )
            }
          >

            <option value="">
              — choose a resume —
            </option>

            {resumes.map((r) => (
              <option
                key={r.id}
                value={r.id}
              >
                #{r.id} ·{" "}
                {r.original_name}
              </option>
            ))}

          </select>

          {resumes.length === 0 && (
            <p className="field-warn">
              No parsed resumes found.{" "}
              <a href="/resume">
                Upload one first →
              </a>
            </p>
          )}
        </div>

        {/* Jobs */}
        <div
          className="field"
          style={{
            marginTop: 20,
          }}
        >

          <label>
            Select Job Posting
          </label>

          <select
            value={jobId}
            onChange={(e) =>
              setJobId(
                e.target.value
              )
            }
          >

            <option value="">
              — choose a job —
            </option>

            {jobs.map((j) => (
              <option
                key={j.id}
                value={j.id}
              >
                #{j.id} · {j.title}
                {j.company
                  ? ` @ ${j.company}`
                  : ""}
              </option>
            ))}

          </select>

          {jobs.length === 0 && (
            <p className="field-warn">
              No jobs found.{" "}
              <a href="/jobs">
                Create one first →
              </a>
            </p>
          )}
        </div>

        {/* Polling state */}
        {taskId && !done ? (

          <div
            className="poll-status"
            style={{
              marginTop: 24,
            }}
          >

            <div className="spinner" />

            <span>
              Evaluating…{" "}
              <StatusChip
                status={
                  pollData?.status ||
                  "processing"
                }
              />
            </span>

          </div>

        ) : (

          <Btn
            onClick={submit}
            loading={submitting}
            style={{
              width: "100%",
              marginTop: 24,
            }}
            disabled={
              !resumeId || !jobId
            }
          >
            Run Evaluation →
          </Btn>

        )}
      </Card>
    </div>
  );
}

/* Result Page */
function EvalResult({
  result,
  onReset,
}) {

  const recColor = {
    Hire: "#00d4ff",
    Improve: "#f0a500",
    Reject: "#ff5a5a",
  };

  const rec =
    result.recommendation ||
    "Improve";

  const totalScore =
    typeof result.total_score ===
    "number"
      ? result.total_score
      : 0;

  const skillsScore =
    typeof result.skills_score ===
    "number"
      ? result.skills_score
      : 0;

  const experienceScore =
    typeof result.experience_score ===
    "number"
      ? result.experience_score
      : 0;

  const keywordScore =
    typeof result.keyword_score ===
    "number"
      ? result.keyword_score
      : 0;

  return (
    <div className="page page--narrow">

      <div className="result-header">

        <h1 className="page-title">
          Evaluation Result
        </h1>

        <button
          className="btn btn--outline"
          onClick={onReset}
        >
          New Evaluation
        </button>

      </div>

      {/* Hero */}
      <Card className="eval-hero">

        <ScoreRing
          score={Math.round(
            totalScore
          )}
          size={140}
        />

        <div className="eval-hero__info">

          <div
            className="rec-badge"
            style={{
              background: `${recColor[rec]}22`,
              color: recColor[rec],
              borderColor: `${recColor[rec]}44`,
            }}
          >
            {rec === "Hire"
              ? "✓ "
              : rec === "Improve"
              ? "⚠ "
              : "✕ "}

            {rec}
          </div>

          <p className="eval-reasoning">
            {result.reasoning}
          </p>

        </div>
      </Card>

      {/* Sub Scores */}
      <div className="sub-scores">

        {[
          {
            label:
              "Skills Match",
            score: skillsScore,
            weight: "45%",
          },
          {
            label:
              "Experience Relevance",
            score:
              experienceScore,
            weight: "30%",
          },
          {
            label:
              "Keyword Coverage",
            score:
              keywordScore,
            weight: "25%",
          },
        ].map(
          ({
            label,
            score,
            weight,
          }) => (
            <Card
              key={label}
              className="sub-score-card"
            >

              <div className="sub-score__top">

                <span className="sub-score__label">
                  {label}
                </span>

                <span className="sub-score__weight">
                  weight {weight}
                </span>

              </div>

              <div className="sub-score__num">
                {Math.round(score)}
                <span>/100</span>
              </div>

              <div className="progress-bar">
                <div
                  className="progress-bar__fill"
                  style={{
                    width: `${score}%`,
                  }}
                />
              </div>

            </Card>
          )
        )}

      </div>

      {/* Skills */}
      <div className="skills-row">

        <Card>

          <h3 className="card-title">
            ✓ Matched Skills (
            {result
              .matched_skills
              ?.length || 0}
            )
          </h3>

          <div className="badge-row">

            {result
              .matched_skills
              ?.length > 0 ? (

              result.matched_skills.map(
                (s) => (
                  <Badge
                    key={s}
                    label={s}
                    variant="match"
                  />
                )
              )

            ) : (

              <p className="muted">
                None matched.
              </p>

            )}

          </div>
        </Card>

        <Card>

          <h3 className="card-title">
            ✕ Missing Skills (
            {result
              .missing_skills
              ?.length || 0}
            )
          </h3>

          <div className="badge-row">

            {result
              .missing_skills
              ?.length > 0 ? (

              result.missing_skills.map(
                (s) => (
                  <Badge
                    key={s}
                    label={s}
                    variant="miss"
                  />
                )
              )

            ) : (

              <p className="muted">
                All required skills
                matched! 🎉
              </p>

            )}

          </div>
        </Card>
      </div>

      {/* AI Feedback */}
      {result.ai_feedback && (

        <Card className="ai-feedback">

          <h3 className="card-title">
            🤖 AI Feedback
          </h3>

          <div className="ai-feedback__body">

            {result.ai_feedback
              .split("\n")
              .filter(Boolean)
              .map((line, i) => (
                <p key={i}>
                  {line}
                </p>
              ))}

          </div>

        </Card>

      )}

      <div className="result-actions">

        <a
          href="/jobs"
          className="btn btn--outline"
        >
          Browse More Jobs
        </a>

        <a
          href="/resume"
          className="btn btn--primary"
        >
          Upload New Resume
        </a>

      </div>
    </div>
  );
}