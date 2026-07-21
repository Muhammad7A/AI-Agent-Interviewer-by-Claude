import type { KnowledgeEdge } from '@oi/contracts';
import type {
  ReportsToEdgeAttributes,
  PartOfEdgeAttributes,
  CollaboratesWithEdgeAttributes,
  ReportsToEdge,
  PartOfEdge,
  CollaboratesWithEdge,
} from './structural-edges';
import type {
  OwnsEdgeAttributes,
  DeliversEdgeAttributes,
  ComposedOfEdgeAttributes,
  DependsOnEdgeAttributes,
  OwnsEdge,
  DeliversEdge,
  ComposedOfEdge,
  DependsOnEdge,
} from './capability-edges';
import type {
  RealizedByEdgeAttributes,
  HasStepEdgeAttributes,
  PrecedesEdgeAttributes,
  PerformedByEdgeAttributes,
  UsesEdgeAttributes,
  ProducesEdgeAttributes,
  ConsumesEdgeAttributes,
  HandsOffViaEdgeAttributes,
  RealizedByEdge,
  HasStepEdge,
  PrecedesEdge,
  PerformedByEdge,
  UsesEdge,
  ProducesEdge,
  ConsumesEdge,
  HandsOffViaEdge,
} from './operational-edges';

export * from './edge-type';
export * from './structural-edges';
export * from './capability-edges';
export * from './operational-edges';

/** Edge-attribute unions per layer (discriminated by `edgeType`). */
export type StructuralEdgeAttributes =
  | ReportsToEdgeAttributes
  | PartOfEdgeAttributes
  | CollaboratesWithEdgeAttributes;

export type CapabilityEdgeAttributes =
  | OwnsEdgeAttributes
  | DeliversEdgeAttributes
  | ComposedOfEdgeAttributes
  | DependsOnEdgeAttributes;

export type OperationalEdgeAttributes =
  | RealizedByEdgeAttributes
  | HasStepEdgeAttributes
  | PrecedesEdgeAttributes
  | PerformedByEdgeAttributes
  | UsesEdgeAttributes
  | ProducesEdgeAttributes
  | ConsumesEdgeAttributes
  | HandsOffViaEdgeAttributes;

/** Every edge-attribute payload the Knowledge context owns. */
export type KnowledgeEdgeAttributes =
  | StructuralEdgeAttributes
  | CapabilityEdgeAttributes
  | OperationalEdgeAttributes;

/** The discriminated union of every typed Knowledge edge. */
export type KnowledgeEdgeUnion =
  | ReportsToEdge
  | PartOfEdge
  | CollaboratesWithEdge
  | OwnsEdge
  | DeliversEdge
  | ComposedOfEdge
  | DependsOnEdge
  | RealizedByEdge
  | HasStepEdge
  | PrecedesEdge
  | PerformedByEdge
  | UsesEdge
  | ProducesEdge
  | ConsumesEdge
  | HandsOffViaEdge;

/** A Knowledge edge whose attributes are any of this context's payloads. */
export type AnyKnowledgeEdge = KnowledgeEdge<KnowledgeEdgeAttributes>;
