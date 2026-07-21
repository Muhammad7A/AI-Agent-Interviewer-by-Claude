import type { NodeAttributes, KnowledgeNode } from '@oi/contracts';
import type { ArtifactFormat } from '../../value-objects/enums';

/** An input/output of an activity — a document, spreadsheet, ticket or dataset. Manual artifact processing is a frequent opportunity site. */
export interface ArtifactAttributes extends NodeAttributes<'Artifact'> {
  readonly format: ArtifactFormat;
}

export type ArtifactNode = KnowledgeNode<ArtifactAttributes>;
