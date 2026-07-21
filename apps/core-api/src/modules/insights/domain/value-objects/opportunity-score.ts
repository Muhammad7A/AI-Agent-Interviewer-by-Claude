import type { Score } from '@oi/contracts';
import type { BusinessValue, ImplementationComplexity } from './scales';

/**
 * A computed, explainable ranking score for an `Opportunity`. Reuses the Shared
 * Kernel `Score` scalar; the qualitative drivers are retained alongside so the
 * ranking is transparent (never an opaque number).
 */
export interface OpportunityScore {
  readonly value: Score;
  readonly businessValue: BusinessValue;
  readonly implementationComplexity: ImplementationComplexity;
  readonly rationale: string;
}
