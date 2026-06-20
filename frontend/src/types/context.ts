export type ContextPackMode = "offline" | "enhanced" | "fallback";

export interface ContextRecommendation {
  path: string;
  reason: string;
  score: number;
}

export interface ContextPack {
  task: string;
  mode: ContextPackMode;
  model: string | null;
  recommendations: ContextRecommendation[];
  prompt: string;
  mentions: string;
  estimatedTokens: number;
  reductionPercent: number;
  providerMessage: string;
  artifactPath: string;
}
