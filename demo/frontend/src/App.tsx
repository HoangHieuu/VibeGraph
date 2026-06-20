import { FormEvent, useState } from "react";

import { login, type SessionView } from "./api";

export function App() {
  const [email, setEmail] = useState("builder@vibegraph.dev");
  const [password, setPassword] = useState("ship-fast");
  const [session, setSession] = useState<SessionView>();
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError("");
    try {
      setSession(await login(email, password));
    } catch (loginError) {
      setSession(undefined);
      setError(loginError instanceof Error ? loginError.message : "Login failed.");
    } finally {
      setPending(false);
    }
  }

  return (
    <main>
      <section className="intro">
        <p>Agent workspace</p>
        <h1>Ship the auth fix without losing the graph.</h1>
        <span>
          This deliberately small project gives VibeGraph a clear route,
          service, error model, test, and agent-tool neighborhood.
        </span>
      </section>

      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button disabled={pending} type="submit">
          {pending ? "Validating…" : "Start session"}
        </button>
        {error ? <p className="error">{error}</p> : null}
        {session ? (
          <div className="success">
            <strong>{session.user}</strong>
            <span>{session.message}</span>
          </div>
        ) : null}
      </form>
    </main>
  );
}
