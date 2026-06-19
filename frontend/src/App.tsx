import { AppHeader } from "./components/AppHeader";
import { GraphBackdrop } from "./components/GraphBackdrop";
import { RuntimeStatus } from "./components/RuntimeStatus";

export function App() {
  return (
    <main className="app-shell">
      <AppHeader />
      <div className="canvas">
        <GraphBackdrop />
        <RuntimeStatus />
        <p className="offline-note">No API key required</p>
      </div>
    </main>
  );
}
