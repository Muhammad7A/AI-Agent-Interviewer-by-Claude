/**
 * Application layer (contracts only) — the cross-context orchestration layer.
 *
 * Wires the six domain contexts into platform use cases without owning domain
 * truth. Depends on domain contracts and the Shared Kernel only; all external AI
 * access goes through the AI Engine ACL (`./ai`); AI output is a proposal that is
 * mapped and validated before becoming domain state (ADR-0008).
 *
 * No behaviour, persistence, infrastructure, HTTP, or SDK usage — handlers are
 * interfaces; their orchestration is implemented later and is testable against
 * port fakes with no infrastructure.
 */
export * from './shared';
export * from './ai';
export * from './use-cases';
export * from './events';
