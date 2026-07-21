import type {
  GraphElementKind,
  KnowledgeNodeId,
  KnowledgeEdgeId,
  IntervieweeRef,
  RoleLabel,
  DepartmentLabel,
} from '@oi/contracts';
import type { KnowledgeNodeType } from '@oi/knowledge';
import type {
  Department,
  Position,
  Employee,
  ReportingLine,
  AnyOfficialArtifact,
  OrgUnitIdentifier,
} from '@oi/organization';

/**
 * Ids re-derived from Organization's Published Language via indexed access.
 * Organization publishes its aggregate *types* but not its branded id value
 * objects, so we recover the branded ids without duplicating them and without
 * modifying that context. (See the seam note in the context README.)
 */
export type OfficialDepartmentId = Department['id'];
export type OfficialPositionId = Position['id'];
export type OfficialEmployeeId = Employee['id'];
export type OfficialReportingLineId = ReportingLine['id'];
export type OfficialArtifactId = AnyOfficialArtifact['id'];
export type OfficialArtifactRefKind = AnyOfficialArtifact['artifactKind'];

/**
 * A reference to an element of the **official** (declared) model. Drift never
 * owns these — it points at them by identity, discriminated by `kind`.
 */
export type OfficialElementRef =
  | { readonly kind: 'OrgUnit'; readonly ref: OrgUnitIdentifier }
  | { readonly kind: 'Position'; readonly id: OfficialPositionId }
  | { readonly kind: 'Employee'; readonly id: OfficialEmployeeId }
  | { readonly kind: 'ReportingLine'; readonly id: OfficialReportingLineId }
  | {
      readonly kind: 'OfficialArtifact';
      readonly artifactKind: OfficialArtifactRefKind;
      readonly id: OfficialArtifactId;
    };

/**
 * A reference to an element of the **discovered** (Knowledge/Transcript) model.
 * Covers graph artifacts *and* the raw discovered identifiers that identity
 * resolution operates on — interviewees and free-text role/department labels.
 */
export type DiscoveredElementRef =
  | { readonly kind: 'GraphNode'; readonly id: KnowledgeNodeId; readonly nodeType?: KnowledgeNodeType }
  | { readonly kind: 'GraphEdge'; readonly id: KnowledgeEdgeId }
  | { readonly kind: 'Interviewee'; readonly ref: IntervieweeRef }
  | { readonly kind: 'RoleLabel'; readonly label: RoleLabel }
  | { readonly kind: 'DepartmentLabel'; readonly label: DepartmentLabel };

/** Convenience: which side of a comparison is which. */
export type ComparisonSide = 'Official' | 'Discovered';

// `GraphElementKind` is re-exported so consumers can align with the Shared Kernel
// substrate vocabulary when interpreting a discovered graph reference.
export type { GraphElementKind };
