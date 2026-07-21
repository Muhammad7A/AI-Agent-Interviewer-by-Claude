/**
 * The consultant-in-the-loop lifecycle state of a graph artifact. The AI
 * proposes (`Proposed`); the consultant disposes. Machine output is never
 * presented as established fact.
 *
 *  - `Proposed`: AI-derived, unreviewed.
 *  - `ConsultantAdded`: human-originated, authoritative from creation.
 *  - `UnderReview`: a consultant has opened it for review.
 *  - `Validated`: consultant-confirmed.
 *  - `Edited`: consultant-corrected (the AI original is preserved).
 *  - `Dismissed`: consultant-rejected (with reason).
 */
export type ValidationState =
  | 'Proposed'
  | 'ConsultantAdded'
  | 'UnderReview'
  | 'Validated'
  | 'Edited'
  | 'Dismissed';
