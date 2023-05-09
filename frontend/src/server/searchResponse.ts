import { SearchResponseFacetCountSchema, SearchResponseHit } from "typesense/lib/Typesense/Documents";
import { Meeting } from "../meetingTypes";
import { MeetingDocument } from "./meetingResponse";

export type Hit = SearchResponseHit<MeetingDocument<boolean>>

export interface SearchResponse {
  response_type: string;
  found: number,
  out_of: number, 
  facet_counts: FacetCount[],
  hits: SearchResponseHit<MeetingDocument<boolean>>[]
}

export interface FacetCount {
  counts: Array<{count: number, value: string}>;
  fieldName: string;
}

/**
 * Meeting JSON given by the API meetingSearch endpoint. Takes in a boolean 
 * generic parameter indicating whether the meeting is cancelled or not. 
 */
export interface MeetingDocumentMetadata<isCancelled extends boolean> {
  id: string;
  body: string;
  /**
   * Date of meeting in seconds since midnight, January 1, 1970 UTC. 
   * Javascript date objects give Epoch time in *milli*seconds, so this value
   * should multiplied by 1000 before being passed into the Date() constructor
   */
  meeting_dt: number; 
  address: string;
  is_cancelled: isCancelled;
  cancelled_dt: isCancelled extends true ? number : null;
}


export const isSearchResponse = (json: any): json is SearchResponse => {
  if (!("response_type" in json) || json?.response_type !== "success") return false;
  if (!("found" in json)) return false
  if (!("out_of" in json)) return false

  // checking that facet_counts is Facet[]
  if (!Array.isArray(json?.facet_counts)) return false
  if (!json.facet_counts.every((elt: any) => isFacet(elt))) return false

  
  // checking that hits is Hit[]
  if (!Array.isArray(json?.hits)) return false
  if (!json.hits.every((elt: any) => isSearchResponseHit(elt))) return false
  return true
}

const isFacet = (json: any): json is SearchResponseFacetCountSchema<MeetingDocument<boolean>> => {
  if (!Array.isArray(json?.counts)) return false

  if (!json.counts.every((countsObj: any) => (
    "count" in countsObj && "value" in countsObj
  ))) return false
  if (!("fieldName" in json)) return false
  return true
}

const isSearchResponseHit = (json: any): json is SearchResponseHit<MeetingDocument<boolean>> => {
  if (!Array.isArray(json?.highlights)) return false

  if (!json.highlights.every((highlight: any) => (
    "field" in highlight && ("snippet" in highlight || "snippets" in highlight)
  ))) return false

  if (!(isMeetingDocumentMetadata(json.document))) return false
  return true
}

export function isMeetingDocumentMetadata(json: any): json is MeetingDocumentMetadata<boolean> {
  if (!("id" in json)) return false
  if (!("body" in json)) return false
  if (!("meeting_dt" in json)) return false
  if (!("address" in json)) return false
  if (!("is_cancelled" in json)) return false
  if (json.is_cancelled && !("cancelled_dt" in json)) return false
  return true
}

export function isCancelled(target: any): target is MeetingDocumentMetadata<true> {
  if (!isMeetingDocumentMetadata(target)) return false
  if (!target.is_cancelled) return false
  if (target.cancelled_dt === null) return false
  return true
}