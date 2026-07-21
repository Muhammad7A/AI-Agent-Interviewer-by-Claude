import type { EngagementId } from '@oi/contracts';
import type { Command, CommandHandler } from '../shared/use-case';

/**
 * Assemble a consultant deliverable from **validated** insights and drift results.
 *
 * NOTE (seam): the Reporting bounded context domain is not yet built, so this use
 * case currently composes Insights + Drift read models into an application-level
 * report DTO. When Reporting exists, this delegates assembly to it. Only
 * `Validated` insights are included; unvalidated items are omitted or flagged.
 */
export interface ProduceConsultantReportCommand extends Command {
  readonly engagementId: EngagementId;
  /** Optional: pin a specific drift assessment (opaque id at the boundary). */
  readonly assessmentId?: string;
}

export interface ConsultantReportSectionDto {
  readonly title: string;
  readonly body: string;
}

export interface ProduceConsultantReportResult {
  readonly reportId: string;
  readonly sections: readonly ConsultantReportSectionDto[];
}

export interface ProduceConsultantReportHandler
  extends CommandHandler<ProduceConsultantReportCommand, ProduceConsultantReportResult> {}
