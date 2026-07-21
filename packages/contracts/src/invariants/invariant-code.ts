/**
 * Stable identifiers for the Shared Kernel invariants — the non-negotiable rules
 * the substrate contracts encode. Factories, guards and tests reference these by
 * code once implementation begins (the enforcing logic does not live in this
 * contracts-only package).
 */
export type InvariantCode = 'N1' | 'N2' | 'N3' | 'N4' | 'N5' | 'E1';
