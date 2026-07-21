/**
 * Qualitative graded scales — the consultant's vocabulary for sizing problems
 * and opportunities. Pure string-literal unions (no runtime footprint). Composite,
 * computed scores (`OpportunityScore`, `RecommendationPriority`) live in their own
 * value objects and reuse the Shared Kernel `Score`.
 */

/** How damaging a pain point is when it occurs. */
export type Severity = 'Low' | 'Moderate' | 'High' | 'Critical';

/** How often a pain point occurs. */
export type Frequency = 'Rare' | 'Occasional' | 'Frequent' | 'Constant';

/** The magnitude of business consequence. */
export type BusinessImpact = 'Minimal' | 'Moderate' | 'Significant' | 'Severe';

/** How time-pressured acting on something is. */
export type Urgency = 'Low' | 'Medium' | 'High' | 'Immediate';

/** Level of risk (of a pain point persisting, or of an intervention). */
export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical';

/** The business value an opportunity would unlock. */
export type BusinessValue = 'Low' | 'Medium' | 'High' | 'Transformational';

/** How hard an opportunity/recommendation is to implement. */
export type ImplementationComplexity = 'Trivial' | 'Low' | 'Medium' | 'High' | 'VeryHigh';
