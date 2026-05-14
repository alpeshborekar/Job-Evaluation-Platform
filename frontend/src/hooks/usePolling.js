import { useState, useEffect, useRef, useCallback } from "react";
export function usePolling(fn, { interval = 2000, enabled = true } = {}) {
  const [data, setData]   = useState(null);
  const [done, setDone]   = useState(false);
  const [error, setError] = useState(null);
  const timerRef          = useRef(null);
  const fnRef             = useRef(fn);
  const intervalRef       = useRef(interval);

  
  useEffect(() => { fnRef.current = fn; }, [fn]);
  useEffect(() => { intervalRef.current = interval; }, [interval]);

  const poll = useCallback(async () => {
    try {
      const r = await fnRef.current();
      setData(r.data);
      if (["completed", "failed"].includes(r.data?.status)) {
        setDone(true);
        if (r.data?.status === "failed") setError(r.data?.error || "Task failed");
      }
    } catch (e) {
      setError(e.message);
      setDone(true);
    }
  }, []);

  useEffect(() => {
    if (!enabled || done) return;
    poll();
    timerRef.current = setInterval(poll, intervalRef.current);
    return () => clearInterval(timerRef.current);
  }, [enabled, done, poll]);

  return { data, done, error };
}