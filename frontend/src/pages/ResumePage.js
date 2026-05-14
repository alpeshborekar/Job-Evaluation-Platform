import {
  useState,
  useRef,
  useCallback,
} from "react";

import { resumeAPI } from "../api/client";

import {
  Btn,
  Badge,
  StatusChip,
  Card,
  toast,
} from "../components/UI";


export default function ResumePage() {

  const [file, setFile] =
    useState(null);

  const [dragging, setDragging] =
    useState(false);

  const [email, setEmail] =
    useState("");

  const [uploading, setUploading] =
    useState(false);

  const [result, setResult] =
    useState(null);

  const inputRef = useRef();


  const onDrop = useCallback((e) => {

    e.preventDefault();

    setDragging(false);

    const f =
      e.dataTransfer?.files?.[0] ||
      e.target.files?.[0];

    if (f) {
      validateAndSet(f);
    }

  }, []);


  const validateAndSet = (f) => {

    const ext = f.name
      .split(".")
      .pop()
      .toLowerCase();

    if (
      !["pdf", "docx"].includes(ext)
    ) {

      toast.error(
        "Only PDF and DOCX files are supported."
      );

      return;
    }

    setFile(f);
  };


  const upload = async () => {

    if (!file) {

      toast.error(
        "Please select a file."
      );

      return;
    }

    setUploading(true);

    try {

      const fd =
        new FormData();

      fd.append(
        "resume",
        file
      );

      if (email) {

        fd.append(
          "email",
          email
        );
      }

      console.log(
        "Uploading resume..."
      );

      const r =
        await resumeAPI.upload(fd);

      console.log(
        "UPLOAD RESPONSE:",
        r.data
      );

      setResult(r.data);

      toast.success(
        "Resume parsed successfully!"
      );

    } catch (err) {

      console.error(err);

      toast.error(
        err?.response?.data?.message ||
        "Upload failed."
      );

    } finally {

      setUploading(false);
    }
  };


  const reset = () => {

    setFile(null);

    setResult(null);

    setEmail("");
  };


  if (result) {

    return (
      <ResumeResult
        result={result}
        onReset={reset}
      />
    );
  }


  return (
    <div className="page page--narrow">

      <h1 className="page-title">
        Upload Resume
      </h1>

      <p className="page-sub">
        Upload a PDF or DOCX —
        we'll parse and extract
        your skills.
      </p>


      <div
        className={`dropzone${
          dragging
            ? " dropzone--active"
            : ""
        }${
          file
            ? " dropzone--filled"
            : ""
        }`}
        onDragOver={(e) => {

          e.preventDefault();

          setDragging(true);
        }}
        onDragLeave={() =>
          setDragging(false)
        }
        onDrop={onDrop}
        onClick={() =>
          !file &&
          inputRef.current?.click()
        }
      >

        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          hidden
          onChange={onDrop}
        />

        {file ? (
          <>
            <div className="dz-icon">
              📄
            </div>

            <p className="dz-name">
              {file.name}
            </p>

            <p className="dz-size">
              {(
                file.size / 1024
              ).toFixed(1)} KB
            </p>

            <button
              className="dz-remove"
              onClick={(e) => {

                e.stopPropagation();

                setFile(null);
              }}
            >
              ✕ Remove
            </button>
          </>
        ) : (
          <>
            <div className="dz-icon">
              ⬆
            </div>

            <p className="dz-label">
              Drag & drop or click to browse
            </p>

            <p className="dz-hint">
              PDF or DOCX · max 10 MB
            </p>
          </>
        )}
      </div>


      <div
        className="field"
        style={{
          marginTop: 20,
        }}
      >

        <label>
          Email report to
          (optional)
        </label>

        <input
          type="email"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
          placeholder="you@example.com"
        />
      </div>


      <Btn
        type="button"
        onClick={upload}
        loading={uploading}
        style={{
          marginTop: 24,
          width: "100%",
        }}
        variant={
          file
            ? "primary"
            : "disabled"
        }
        disabled={!file}
      >
        Parse Resume →
      </Btn>
    </div>
  );
}



function ResumeResult({
  result,
  onReset,
}) {

  return (
    <div className="page page--narrow">

      <div className="result-header">

        <h1 className="page-title">
          Parse Complete ✓
        </h1>

        <button
          className="btn btn--outline"
          onClick={onReset}
        >
          Upload Another
        </button>
      </div>


      <Card className="result-meta">

        <div className="meta-row">

          <span className="meta-label">
            File
          </span>

          <span>
            {result.filename ||
              result.original_name}
          </span>
        </div>


        <div className="meta-row">

          <span className="meta-label">
            Word Count
          </span>

          <span>
            {result.word_count
              ?.toLocaleString() || "—"}
          </span>
        </div>


        <div className="meta-row">

          <span className="meta-label">
            Status
          </span>

          <StatusChip
            status={
              result.status ||
              result.parse_status
            }
          />
        </div>


        <div className="meta-row">

          <span className="meta-label">
            Resume ID
          </span>

          <span className="mono">
            #{result.id}
          </span>
        </div>
      </Card>


      <Card>

        <h3 className="card-title">

          Skills Detected (
          {result.skills_found
            ?.length || 0}
          )
        </h3>

        <div className="badge-row">

          {result.skills_found
            ?.length > 0 ? (

            result.skills_found.map(
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
              No skills detected.
            </p>
          )}
        </div>
      </Card>


      <div className="result-actions">

        <a
          href={`/evaluate?resume_id=${result.id}`}
          className="btn btn--primary"
        >
          Evaluate Against a Job →
        </a>
      </div>
    </div>
  );
}