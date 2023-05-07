import { MeetingDocumentMetadata, isMeetingDocumentMetadata } from "./searchResponse"

export interface MeetingResponse {
  result: "success";
  meeting: MeetingDocument<boolean>
}

export interface MeetingDocument<IsCancelled extends boolean> extends MeetingDocumentMetadata<IsCancelled> {
  cancelled_reason: IsCancelled extends true ? string : null;
  latestAgenda: string[] | null;
  latestAgendaLink: string | null;
  latestMinutes: string[] | null;
  latestMinutesLink: string | null;
  contactPerson: string
  contactEmail: string
  contactPhone: string
}

export function isMeetingResponse(json: any): json is MeetingResponse {
  if (!("result" in json) || json?.result !== "success") return false;
  if (!("meeting" in json)) return false;
  if (!(isMeetingDocument(json.meeting))) return false
  return true
}

function isMeetingDocument(json: any): json is MeetingDocument<boolean> {
  if (!isMeetingDocumentMetadata(json)) return false

  if (!("cancelled_reason" in json)) return false
  if (!("latestAgenda" in json)) return false
  if (!("latestAgendaLink" in json)) return false
  if (json.latestAgenda === null && json.latestAgendaLink != null) return false
  if (!("latestMinutes" in json)) return false
  if (!("latestMinutesLink" in json)) return false
  if (json.latestMinutes === null && json.latestMinutesLink != null) return false
  if (!("contactPerson" in json)) return false
  if (!("contactEmail" in json)) return false
  if (!("contactPhone" in json)) return false
  return true
}

export function isCancelled(target: any): target is MeetingDocument<true> {
  if (!isMeetingDocument(target)) return false
  if (!target.is_cancelled) return false
  if (target.cancelled_dt === null) return false
  return true
}