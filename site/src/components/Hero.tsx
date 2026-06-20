import { InstallCommand } from "./InstallCommand";
import { ProductMockup } from "./ProductMockup";

const GITHUB_URL = "https://github.com/HoangHieuu/VibeGraph";

export function Hero() {
  return (
    <section className="hero shell" id="top">
      <div className="hero-copy">
        <h1>See the codebase before your agent changes it.</h1>
        <p>
          VibeGraph turns any local repository into a live dependency map,
          catches breakage as it happens, and prepares the smallest useful
          context for your AI coding tool.
        </p>
        <div className="hero-actions">
          <a className="button" href="#install">
            Run VibeGraph
          </a>
          <a className="text-link arrow-link" href={GITHUB_URL}>
            View on GitHub <span aria-hidden="true">↗</span>
          </a>
        </div>
        <InstallCommand />
      </div>
      <ProductMockup />
    </section>
  );
}
