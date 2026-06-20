export type ReadmeMode = "offline" | "enhanced" | "fallback";

export interface ReadmeModule {
  name: string;
  summary: string;
  files: string[];
  entrypoints: string[];
}

export interface GeneratedReadme {
  mode: ReadmeMode;
  model: string | null;
  projectName: string;
  overview: string;
  architecture: string;
  modules: ReadmeModule[];
  entrypoints: string[];
  keyFiles: string[];
  commands: string[];
  warnings: string[];
  mermaid: string;
  markdown: string;
  providerMessage: string;
  artifactPath: string;
}
