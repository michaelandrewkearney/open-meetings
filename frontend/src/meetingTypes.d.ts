

/**
 * Manages search state in the React app. 
 * 
 * A `null` `search` property indicates the search has been cleared, or no 
 * search has been performed yet.
 * 
 * `null` values for the `dateStart` and `dateEnd` properties indicates no filter
 * is selected for the corresponding date range boundary.
 */
export interface SearchState {
  search: Search | null;
  dateStart: Date | null;
  dateEnd: Date | null;
}

/**
 * The search returned from the Open Meetings API. 
 */
interface Search {
  /** Keyphrase to search on */
  readonly keyphrase: string;
  /** 
   * Public body to filter results on. A `null` value indicates meetings from 
   * all public bodies should be returned.
   */
  readonly selectedBody: string | null;
  /** Meetings returned by the current search */
  readonly results: readonly MeetingResult[];
  /**  
   * Map of body names to counts. Should only change when keyphrase is altered,
   * **not** when the selectedBody changes
   */
  readonly bodyFacetMap: Map<string, number>;
  /** Info about the number of results found, out of the total number of meetings */
  readonly resultsInfo: { found: number; outOf: number };
}

/**
 * Abstract interface for common properties of PlannedMeetingResults and 
 * CancelledMeetingResults.
 * 
 * Objects should **never** have this interface. 
 */
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

/**
 * Meeting result objects used in the React app. 
 * 
 * All MeetingDocumentMetadata objects should be converted to MeetingResult 
 * objects within a SearchFunction before being passed to the React app. 
 * This is useful because changes to the API interface now only require 
 * refactoring a single function, rather than the entire web app.
 */
export type MeetingResult = PlannedMeetingResult | CancelledMeetingResult