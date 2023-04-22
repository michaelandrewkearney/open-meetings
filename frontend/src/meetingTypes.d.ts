export interface SearchState {
  search: Search | null;
  dateStart: Date | null;
  dateEnd: Date | null;
}

interface Search {
  readonly keyphrase: string;
  // Map of body names to counts
  readonly bodyFacetMap: Map<string, number>;
  resultsInfo: { found: number; outOf: number };
  results: readonly MeetingResult[];
  selectedBody: string | null;
}


interface AbstractMeetingResult {
  readonly id: string;
  readonly body: string;
  readonly meetingDate: Date;
  readonly address: string;
  readonly highlights: readonly ResultHighlight[]
}

interface ResultHighlight {
  field: string
  snippet: string
}

export interface PlannedMeetingResult extends AbstractMeetingResult {
  readonly isCancelled: false;
}

export interface CancelledMeetingResult extends AbstractMeetingResult {
  readonly isCancelled: true;
  readonly cancelledDate: Date;
}

export type MeetingResult = PlannedMeetingResult | CancelledMeetingResult