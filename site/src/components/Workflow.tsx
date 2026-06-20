const steps = [
  {
    number: "01",
    title: "Scan locally",
    body: "Python, JavaScript, JSX, TypeScript, and TSX stay on your machine.",
  },
  {
    number: "02",
    title: "Map dependencies",
    body: "Imports become a directed graph with files, modules, warnings, and neighborhoods.",
  },
  {
    number: "03",
    title: "Describe the task",
    body: "Fix login error handling in auth_routes.py",
  },
  {
    number: "04",
    title: "Copy focused context",
    body: "Route, service, error model, and relevant test—written to .vibegraph/context.md.",
  },
];

export function Workflow() {
  return (
    <section className="workflow shell" id="workflow">
      <div className="section-heading">
        <h2>From prompt to precise context.</h2>
        <p>
          VibeGraph queries the repository graph before recommending what your
          coding agent should see.
        </p>
      </div>
      <ol className="workflow-steps">
        {steps.map((step) => (
          <li key={step.number}>
            <span>{step.number}</span>
            <strong>{step.title}</strong>
            <p>{step.body}</p>
          </li>
        ))}
      </ol>
      <div className="context-output">
        <div>
          <span>Task</span>
          <strong>Fix login error handling in auth_routes.py</strong>
        </div>
        <ul>
          <li>auth_routes.py</li>
          <li>session_service.py</li>
          <li>errors.py</li>
          <li>test_auth_flow.py</li>
        </ul>
        <code>.vibegraph/context.md</code>
      </div>
    </section>
  );
}
