import type { KnowledgeNode } from '@oi/contracts';
import type {
  DepartmentAttributes,
  TeamAttributes,
  RoleAttributes,
  PersonAttributes,
  DepartmentNode,
  TeamNode,
  RoleNode,
  PersonNode,
} from './structural';
import type {
  ProcessAttributes,
  CapabilityAttributes,
  ProcessNode,
  CapabilityNode,
} from './capability';
import type {
  WorkflowAttributes,
  ActivityAttributes,
  HandoffAttributes,
  SystemAttributes,
  ArtifactAttributes,
  WorkflowNode,
  ActivityNode,
  HandoffNode,
  SystemNode,
  ArtifactNode,
} from './operational';

export * from './node-type';
export * from './structural';
export * from './capability';
export * from './operational';

/** Self-discriminating attribute unions (keyed by `nodeType`), per layer. */
export type StructuralNodeAttributes =
  | DepartmentAttributes
  | TeamAttributes
  | RoleAttributes
  | PersonAttributes;

export type CapabilityNodeAttributes = ProcessAttributes | CapabilityAttributes;

export type OperationalNodeAttributes =
  | WorkflowAttributes
  | ActivityAttributes
  | HandoffAttributes
  | SystemAttributes
  | ArtifactAttributes;

/** Every node-attribute payload the Knowledge context owns. */
export type KnowledgeNodeAttributes =
  | StructuralNodeAttributes
  | CapabilityNodeAttributes
  | OperationalNodeAttributes;

/** The discriminated union of every typed Knowledge node. */
export type KnowledgeNodeUnion =
  | DepartmentNode
  | TeamNode
  | RoleNode
  | PersonNode
  | ProcessNode
  | CapabilityNode
  | WorkflowNode
  | ActivityNode
  | HandoffNode
  | SystemNode
  | ArtifactNode;

/** A Knowledge node whose attributes are any of this context's payloads. */
export type AnyKnowledgeNode = KnowledgeNode<KnowledgeNodeAttributes>;
