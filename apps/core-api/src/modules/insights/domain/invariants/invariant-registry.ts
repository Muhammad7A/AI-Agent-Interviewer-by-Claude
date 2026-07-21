import type { InvariantSpec } from '@oi/contracts';
import type { InsightsInvariantCode } from './invariant-code';

/**
 * The Insights context's invariant registry — declarative data, not logic —
 * reusing the Shared Kernel's generic `InvariantSpec` (no duplication). These
 * encode the design principle that **Insights owns interpretation, never truth**:
 * every diagnostic object is grounded in Knowledge artifacts and immutable
 * evidence, and nothing becomes authoritative until validated.
 */
export const INSIGHTS_INVARIANTS = {
  INS1: {
    code: 'INS1',
    name: 'Pain references knowledge',
    statement: 'Every PainPoint references at least one Knowledge artifact (affectedKnowledgeArtifacts is non-empty).',
    appliesTo: ['PainPoint'],
  },
  INS2: {
    code: 'INS2',
    name: 'Opportunity resolves pain',
    statement: 'Every Opportunity resolves one or more PainPoints (addressedPainPointIds is non-empty).',
    appliesTo: ['Opportunity'],
  },
  INS3: {
    code: 'INS3',
    name: 'Recommendation targets opportunity',
    statement: 'Every Recommendation targets at least one Opportunity (targetOpportunityIds is non-empty).',
    appliesTo: ['Recommendation'],
  },
  INS4: {
    code: 'INS4',
    name: 'Traceable to evidence',
    statement:
      'Every Insights artifact is traceable to immutable EvidenceRefs — directly via its evidence, or transitively through the artifacts it references (reuses Shared Kernel N1/E1).',
    appliesTo: ['Observation', 'Finding', 'PainPoint', 'Opportunity', 'Recommendation'],
  },
  INS5: {
    code: 'INS5',
    name: 'Recommendations require findings',
    statement:
      'A Recommendation cannot exist without supporting Findings: it targets Opportunities that resolve PainPoints whose supportingFindingIds are non-empty.',
    appliesTo: ['Recommendation', 'PainPoint', 'Finding'],
  },
  INS6: {
    code: 'INS6',
    name: 'No orphan diagnostic objects',
    statement:
      'Every diagnostic object references its required upstream: Observation→Knowledge artifact, Finding→Observation, PainPoint→Finding, DiagnosticCluster→PainPoint, Opportunity→PainPoint, Recommendation→Opportunity, RecommendationBundle→Recommendation.',
    appliesTo: [
      'Observation',
      'Finding',
      'PainPoint',
      'DiagnosticCluster',
      'Opportunity',
      'Recommendation',
      'RecommendationBundle',
    ],
  },
  INS7: {
    code: 'INS7',
    name: 'AI proposes, domain validates',
    statement:
      'AI never creates authoritative domain objects: AI-authored artifacts enter with validation.state = Proposed; only Validated or ConsultantAdded artifacts are part of the domain (reuses Shared Kernel G4).',
    appliesTo: ['Observation', 'Finding', 'PainPoint', 'Opportunity', 'Recommendation'],
  },
} as const satisfies Record<InsightsInvariantCode, InvariantSpec<InsightsInvariantCode>>;
