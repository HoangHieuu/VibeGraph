import { Mark } from "./Mark";

const GITHUB_URL = "https://github.com/HoangHieuu/VibeGraph";

export function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label="VibeGraph home">
        <Mark />
        <span>VibeGraph</span>
      </a>
      <nav aria-label="Primary navigation">
        <a href="#workflow">How it works</a>
        <a href="#features">Features</a>
        <a href="#demo">Demo</a>
      </nav>
      <div className="header-actions">
        <a className="text-link" href={GITHUB_URL}>
          GitHub
        </a>
        <a className="button button-small" href="#install">
          Get started
        </a>
      </div>
    </header>
  );
}
