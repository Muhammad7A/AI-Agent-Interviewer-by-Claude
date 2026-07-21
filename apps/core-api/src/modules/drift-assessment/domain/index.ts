/**
 * Drift/Assessment bounded context — domain layer (contracts only).
 *
 * The platform's comparative-intelligence layer: it compares declared official
 * truth (Organization) against discovered reality (Knowledge/Transcript/Insights)
 * and owns the *comparison* — never the compared models. It preserves the
 * distinction (Organization owns declared truth, Knowledge owns discovered
 * reality, Drift owns the comparison), references both by ref VOs, and treats
 * identity resolution as probabilistic hypotheses that are explainable and
 * validated before becoming authoritative.
 *
 * Reads only the Published Language of the Shared Kernel (`@oi/contracts`),
 * Knowledge (`@oi/knowledge`), Transcript (`@oi/transcript`), Insights
 * (`@oi/insights`), and Organization (`@oi/organization`). Ids reuse `Brand`;
 * confidences reuse the kernel `Confidence`; scores reuse `Score`; risk reuses
 * Insights' `RiskLevel`; events reuse `DomainEvent`; invariants reuse
 * `InvariantSpec` — no duplication. No behaviour, persistence, infrastructure,
 * application services, or presentation.
 *
 * The curated external surface is `./published-language`.
 */
export * from './value-objects';
export * from './entities';
export * from './aggregates';
export * from './repositories';
export * from './services';
export * from './events';
export * from './invariants';
export * from './read-models';
