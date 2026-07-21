import type { Score } from '@oi/contracts';

/** Organizational maturity band. */
export type MaturityLevel = 'Initial' | 'Developing' | 'Defined' | 'Managed' | 'Optimizing';

/** AI-transformation readiness band. */
export type ReadinessLevel = 'NotReady' | 'Emerging' | 'Ready' | 'Advanced';

/** How far discovered reality has drifted from declared intent (0 = aligned, 1 = fully drifted). Reuses the Shared Kernel `Score`. */
export interface DriftScore {
  readonly value: Score;
  readonly rationale: string;
}

/** How aligned official and discovered are (the complement of drift). */
export interface AlignmentScore {
  readonly value: Score;
  readonly rationale: string;
}

/** Organizational maturity, scored and banded. */
export interface MaturityScore {
  readonly value: Score;
  readonly level: MaturityLevel;
}

/** AI-transformation readiness, scored and banded. */
export interface ReadinessScore {
  readonly value: Score;
  readonly level: ReadinessLevel;
}
