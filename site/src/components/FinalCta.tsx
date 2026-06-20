import { InstallCommand } from "./InstallCommand";
import { Mark } from "./Mark";

const GITHUB_URL = "https://github.com/HoangHieuu/VibeGraph";

export function FinalCta() {
  return (
    <section className="final-section" id="demo">
      <div className="final-graph" aria-hidden="true">
        {Array.from({ length: 10 }, (_, index) => (
          <i key={index} />
        ))}
      </div>
      <div className="final-inner shell" id="install">
        <h2>Map the repo. Give your agent less, better context.</h2>
        <p>
          Run VibeGraph locally in any Python, JavaScript, or TypeScript
          project.
        </p>
        <InstallCommand prominent />
        <a className="text-link arrow-link" href={GITHUB_URL}>
          Open GitHub <span aria-hidden="true">↗</span>
        </a>
      </div>
      <footer className="site-footer shell">
        <div>
          <span className="brand">
            <Mark />
            VibeGraph
          </span>
          <p>Live codebase maps for AI-powered builders.</p>
        </div>
        <div className="footer-links">
          <a href={GITHUB_URL}>GitHub</a>
          <a href={`${GITHUB_URL}#readme`}>Documentation</a>
          <a href={`${GITHUB_URL}/blob/main/LICENSE`}>MIT License</a>
        </div>
        <span>© 2026 vibedev</span>
      </footer>
    </section>
  );
}
