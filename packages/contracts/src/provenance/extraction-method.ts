/**
 * Reproducibility metadata for machine-extracted evidence: which model and
 * prompt produced it. Present on machine-derived evidence; absent on
 * `ConsultantAsserted` evidence.
 */
export interface ExtractionMethod {
  readonly model: string;
  readonly version: string;
  readonly promptRef: string;
}
