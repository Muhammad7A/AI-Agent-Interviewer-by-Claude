import type { OrganizationId } from '@oi/contracts';
import type { ComparisonRule } from '../aggregates/comparison-rule';
import type { ComparisonRuleId } from '../value-objects/ids';

/** **Repository port** for `ComparisonRule` aggregates (the comparison catalog). */
export interface ComparisonRuleRepository {
  findById(id: ComparisonRuleId): Promise<ComparisonRule | null>;
  save(rule: ComparisonRule): Promise<void>;
  findEnabled(organizationId: OrganizationId): Promise<readonly ComparisonRule[]>;
  nextIdentity(): ComparisonRuleId;
}
