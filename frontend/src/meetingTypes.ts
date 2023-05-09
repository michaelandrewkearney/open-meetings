import { isCancelled } from "./server/searchResponse";

export interface SearchFilters {
  readonly body: string | null;
  readonly dateStart: Date | null;
  readonly dateEnd: Date | null;
}

/**
 * The search returned from the Open Meetings API. 
 */
export interface SearchResults {
  /** 
   * Public body to filter results on. A `null` value indicates meetings from 
   * all public bodies should be returned.
   */

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
  readonly highlights?: ResultHighlight[]
  readonly latestAgendaPreview?: string;
}

export interface StringFieldHighlight {
  field: string, 
  snippet: string,
}

export interface ArrayFieldHighlight {
  field: string, 
  snippets: string[],
}

export type ResultHighlight = StringFieldHighlight | ArrayFieldHighlight

export interface PlannedMeetingResult extends AbstractMeetingResult {
  readonly isCancelled: false;
}


export interface CancelledMeetingResult extends AbstractMeetingResult {
  readonly isCancelled: true;
  readonly cancelledDate: Date;
}

interface AbstractMeeting {
  readonly id: string;
  readonly body: string;
  readonly meetingDate: Date;
  readonly filingDate: Date;
  readonly address: string;
  readonly is_emergency: boolean;
  readonly is_annual_calendar: boolean;
  readonly is_public_notice: boolean;
  readonly latestAgenda: string[] | null;
  readonly latestAgendaLink: string | null;
  readonly latestMinutes: string[] | null; 
  readonly latestMinutesLink: string | null;
  readonly contactPerson: string; 
  readonly contactEmail: string;
  readonly contactPhone: string;
}

interface PlannedMeeting extends AbstractMeeting {
  readonly isCancelled: false;
}

interface CancelledMeeting extends AbstractMeeting {
  readonly isCancelled: true;
  readonly cancelledDate: Date;
  readonly cancelledReason: string;
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

/**
 * Meeting type used to represent all data about a meeting. 
 * 
 * Unlike MeetingResult, Meeting objects contain fields for meeting minutes, 
 * agenda, and contact information
 */
export type Meeting = PlannedMeeting | CancelledMeeting

function isAbstractMeeting(target: any): target is AbstractMeeting {
  if (!("id" in target)) return false
  if (!("body" in target)) return false
  if (!("meetingDate" in target)) return false
  if (!("address" in target)) return false
  if (!("is_emergency" in target)) return false
  if (!("is_annual_calendar" in target)) return false
  if (!("is_public_notice" in target)) return false
  if (!("latestAgenda" in target)) return false
  if (!("latestAgendaLink" in target)) return false
  if (!("latestMinutes" in target)) return false
  if (!("latestMinutesLink" in target)) return false
  if (!("contactPerson" in target)) return false
  if (!("contactEmail" in target)) return false
  if (!("contactPhone" in target)) return false
  return true
}

function isPlannedMeeting(target: any): target is PlannedMeeting {
  if (!(isAbstractMeeting(target))) return false
  if (!("isCancelled" in target && target.isCancelled === false)) return false
  return true
}

function isCancelledMeeting(target: any): target is PlannedMeeting {
  if (!(isAbstractMeeting(target))) return false
  if (!("isCancelled" in target && target.isCancelled === true)) return false
  if (!("cancelledDate" in target)) return false
  if (!("cancelledReason" in target)) return false
  return true
}

export function isMeeting(target: any): target is Meeting {
  return isPlannedMeeting(target) || isCancelledMeeting(target)
}