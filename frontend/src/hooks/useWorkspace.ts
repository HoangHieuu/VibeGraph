import { useCallback, useEffect, useState } from "react";

import {
  fetchWarnings,
  loadWorkspace,
  rescanGraph,
  subscribeWorkspaceEvents,
} from "../api/graph";
import type {
  GraphDocument,
  GraphWarning,
  ProjectSummary,
} from "../types/graph";

interface WorkspaceState {
  project: ProjectSummary | null;
  graph: GraphDocument | null;
  warnings: GraphWarning[];
  loading: boolean;
  rescanning: boolean;
  connected: boolean;
  error: string | null;
}

export function useWorkspace() {
  const [state, setState] = useState<WorkspaceState>({
    project: null,
    graph: null,
    warnings: [],
    loading: true,
    rescanning: false,
    connected: false,
    error: null,
  });

  useEffect(() => {
    const controller = new AbortController();
    void loadWorkspace()
      .then((workspace) => {
        if (!controller.signal.aborted) {
          setState((current) => ({
            ...current,
            ...workspace,
            loading: false,
            rescanning: false,
            error: null,
          }));
        }
      })
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setState((current) => ({
            ...current,
            loading: false,
            error: error instanceof Error ? error.message : "Unable to load graph.",
          }));
        }
      });
    return () => controller.abort();
  }, []);

  useEffect(
    () =>
      subscribeWorkspaceEvents({
        onStatusChange: (connected) =>
          setState((current) => ({ ...current, connected })),
        onEvent: (event) => {
        if (event.type === "graph_updated") {
          setState((current) => ({
            ...current,
            graph: event.graph,
            warnings: event.warnings,
            project: current.project
              ? { ...current.project, stats: event.graph.stats }
              : current.project,
          }));
          return;
        }
        setState((current) => ({
          ...current,
          warnings: current.warnings.some(
            (warning) =>
              warning.type === event.warning.type &&
              warning.source === event.warning.source &&
              warning.target === event.warning.target &&
              warning.symbol === event.warning.symbol,
          )
            ? current.warnings
            : [...current.warnings, event.warning],
        }));
        },
      }),
    [],
  );

  const rescan = useCallback(async () => {
    setState((current) => ({ ...current, rescanning: true, error: null }));
    try {
      const [graph, warnings] = await Promise.all([
        rescanGraph(),
        fetchWarnings(),
      ]);
      setState((current) => ({
        ...current,
        graph,
        warnings,
        project: current.project
          ? { ...current.project, stats: graph.stats }
          : current.project,
        rescanning: false,
      }));
    } catch (error) {
      setState((current) => ({
        ...current,
        rescanning: false,
        error: error instanceof Error ? error.message : "Unable to rescan.",
      }));
    }
  }, []);

  return { ...state, rescan };
}
