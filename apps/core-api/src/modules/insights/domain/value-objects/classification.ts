/**
 * Diagnostic classification vocabulary.
 */

/** The consulting question "people, process, or technology?" as a modeled value. */
export type PainCategory = 'People' | 'Process' | 'Technology';

/** Whether a pain point is a surface symptom or an underlying root cause. */
export type PainNature = 'Symptom' | 'RootCause';

/** Whether a diagnostic conclusion was directly stated or structurally inferred. */
export type DiagnosticOrigin = 'Stated' | 'Inferred';
