import type { DomainEvent } from '@oi/contracts';
import type {
  DriftAssessmentId,
  DriftFindingId,
  MappingHypothesisId,
  BaselineSnapshotId,
} from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';
import type { GapSeverity } from '../value-objects/gap-scales';
import type { RiskLevel } from '../value-objects/risk';

/** Drift/Assessment-context domain events, all extending the Shared Kernel `DomainEvent` envelope. */

export type DriftAssessmentStarted = DomainEvent<
  'drift.assessment.started',
  { readonly assessmentId: DriftAssessmentId; readonly baselineSnapshotId: BaselineSnapshotId }
>;

export type MappingHypothesisProposed = DomainEvent<
  'drift.mapping.proposed',
  { readonly mappingId: MappingHypothesisId }
>;

export type MappingHypothesisValidated = DomainEvent<
  'drift.mapping.validated',
  { readonly mappingId: MappingHypothesisId }
>;

export type MappingHypothesisRejected = DomainEvent<
  'drift.mapping.rejected',
  { readonly mappingId: MappingHypothesisId; readonly reason: string }
>;

export type DriftDetected = DomainEvent<
  'drift.detected',
  { readonly findingId: DriftFindingId; readonly category: DriftCategory }
>;

export type DriftSeverityUpdated = DomainEvent<
  'drift.severity.updated',
  { readonly findingId: DriftFindingId; readonly severity: GapSeverity }
>;

export type AlignmentImproved = DomainEvent<
  'drift.alignment.improved',
  { readonly assessmentId: DriftAssessmentId; readonly findingId: DriftFindingId }
>;

export type BaselineRecalculated = DomainEvent<
  'drift.baseline.recalculated',
  { readonly assessmentId: DriftAssessmentId; readonly baselineSnapshotId: BaselineSnapshotId }
>;

export type RiskEscalated = DomainEvent<
  'drift.risk.escalated',
  { readonly findingId: DriftFindingId; readonly level: RiskLevel }
>;

export type AssessmentCompleted = DomainEvent<
  'drift.assessment.completed',
  { readonly assessmentId: DriftAssessmentId }
>;

/** Discriminated union of the Drift/Assessment context's domain events. */
export type DriftAssessmentDomainEvent =
  | DriftAssessmentStarted
  | MappingHypothesisProposed
  | MappingHypothesisValidated
  | MappingHypothesisRejected
  | DriftDetected
  | DriftSeverityUpdated
  | AlignmentImproved
  | BaselineRecalculated
  | RiskEscalated
  | AssessmentCompleted;
