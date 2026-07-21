import type { InvariantSpec } from '@oi/contracts';
import type { KnowledgeInvariantCode } from './invariant-code';

/**
 * The Knowledge context's invariant registry — declarative data, not logic —
 * reusing the Shared Kernel's generic `InvariantSpec` (no duplication). These
 * extend, and never contradict, the substrate invariants (N1–N5, E1).
 */
export const KNOWLEDGE_INVARIANTS = {
  K1: {
    code: 'K1',
    name: 'Merge preserves provenance',
    statement:
      'Merging two nodes preserves identity and unions their evidence; no provenance is lost.',
    appliesTo: ['KnowledgeNode', 'NodeMerge'],
  },
  K2: {
    code: 'K2',
    name: 'Contradictions recorded',
    statement:
      'Conflicting evidence is recorded as a Contradiction, never silently resolved; a consultant resolves it via validation.',
    appliesTo: ['Contradiction', 'Evidence'],
  },
  K3: {
    code: 'K3',
    name: 'In-engagement resolution',
    statement: 'A Claim resolves only into nodes and edges within its own engagement.',
    appliesTo: ['Claim'],
  },
  C1: {
    code: 'C1',
    name: 'Claim evidence is stated',
    statement:
      "A Claim's evidence is of kind 'Stated' — claims are atomic assertions drawn directly from a transcript segment.",
    appliesTo: ['Claim'],
  },
  C2: {
    code: 'C2',
    name: 'Claim resolution consistency',
    statement:
      "A 'Resolved' Claim has a non-empty resolvedInto; 'Unresolved' and 'Rejected' claims have none.",
    appliesTo: ['Claim'],
  },
} as const satisfies Record<KnowledgeInvariantCode, InvariantSpec<KnowledgeInvariantCode>>;
