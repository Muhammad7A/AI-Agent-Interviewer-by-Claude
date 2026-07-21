/**
 * The lifecycle status of a recorded `Contradiction`.
 *  - `Open`: conflicting evidence stands unresolved (the default; K2).
 *  - `Resolved`: a consultant has adjudicated it through validation.
 */
export type ContradictionStatus = 'Open' | 'Resolved';
