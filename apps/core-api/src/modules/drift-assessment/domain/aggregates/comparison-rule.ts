import type { OrganizationId } from '@oi/contracts';
import type { ComparisonRuleId } from '../value-objects/ids';
import type { DriftCategory } from '../value-objects/drift-category';

/**
 * **Aggregate Root.** A declarative rule that defines *how* an official kind is
 * compared against a discovered kind and what the resulting drift category is.
 * The configurable catalog `DriftClassificationPolicy` consults; it holds no
 * comparison outcomes, only the rule.
 */
export interface ComparisonRule {
  readonly id: ComparisonRuleId;
  readonly organizationId: OrganizationId;
  readonly category: DriftCategory;
  readonly name: string;
  readonly description: string;
  /** The official element kind this rule compares (e.g. "OfficialWorkflow"). */
  readonly officialElementKind: string;
  /** The discovered element kind it is compared against (e.g. "Workflow"). */
  readonly discoveredElementKind: string;
  readonly enabled: boolean;
}
