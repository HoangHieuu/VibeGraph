import { FinalCta } from "./components/FinalCta";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { ProductProof } from "./components/ProductProof";
import { Workflow } from "./components/Workflow";

export function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <Workflow />
        <ProductProof />
        <FinalCta />
      </main>
    </>
  );
}
