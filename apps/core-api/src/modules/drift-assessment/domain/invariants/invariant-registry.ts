import type { InvariantSpec } from '@oi/contracts';
import type { DriftInvariantCode } from './invariant-code';

/**
 * The Drift/Assessment context's invariant registry — declarative data, not logic
 * — reusing the Shared Kernel's generic `InvariantSpec` (no duplication). These
 * encode the principle that this context owns the *comparison*: it never asserts
 * evidence-less certainty and never collapses the official and discovered models.
 */
export const DRIFT_INVARIANTS = {
  DRIFT1: {
    code: 'DRIFT1',
    name: 'Finding references both sides',
    statement: 'Every DriftFinding references both an official artifact and a discovered artifact.',
    appliesTo: ['DriftFinding'],
  },
  DRIFT2: {
    code: 'DRIFT2',
    name: 'Assessment has a baseline',
    statement: 'Every DriftAssessment has a baseline version (BaselineVersionRef).',
    appliesTo: ['DriftAssessment'],
  },
  DRIFT3: {
    code: 'DRIFT3',
    name: 'Mapping has confidence',
    statement: 'Every MappingHypothesis has a confidence score (MappingConfidence).',
    appliesTo: ['MappingHypothesis'],
  },
  DRIFT4: {
    code: 'DRIFT4',
    name: 'Traceable evidence',
    statement:
      'No drift result exists without traceable evidence: every DriftFinding and AlignmentGap carries at least one EvidenceRef, resolvable to immutable transcript segments.',
    appliesTo: ['DriftFinding', 'AlignmentGap'],
  },
  DRIFT5: {
    code: 'DRIFT5',
    name: 'Explainable results',
    statement:
      'Identity resolution may be probabilistic, but validated findings and mappings must be explainable (rationale/explanation present).',
    appliesTo: ['MappingHypothesis', 'DriftFinding', 'AlignmentGap'],
  },
  DRIFT6: {
    code: 'DRIFT6',
    name: 'Compatible scopes',
    statement:
      'An assessment cannot compare incompatible scopes: its organization/engagement must match the baseline snapshot organization.',
    appliesTo: ['DriftAssessment', 'BaselineSnapshot'],
  },
  DRIFT7: {
    code: 'DRIFT7',
    name: 'History remains queryable',
    statement:
      'Historical assessments remain queryable: baselines are immutable snapshots and superseded assessments are retained, never deleted.',
    appliesTo: ['DriftAssessment', 'BaselineSnapshot'],
  },
  DRIFT8: {
    code: 'DRIFT8',
    name: 'AI proposes, domain validates',
    statement:
      'AI never creates authoritative drift artifacts: findings, gaps and mappings enter as Proposed; only validated comparisons become authoritative (reuses Shared Kernel G4).',
    appliesTo: ['DriftFinding', 'AlignmentGap', 'MappingHypothesis'],
  },
} as const satisfies Record<DriftInvariantCode, InvariantSpec<DriftInvariantCode>>;
