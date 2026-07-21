import type { Brand } from '@oi/contracts';

/** A diarization label for a speaker within a transcript (e.g. "Speaker 1"), stable before the speaker is resolved to an interviewee. */
export type SpeakerLabel = Brand<string, 'SpeakerLabel'>;
