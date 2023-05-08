import { BASE_URL } from "../config";
import { Meeting } from "../meetingTypes";
import { MeetingDocument, MeetingResponse, isMeetingResponse } from "./meetingResponse";
import { isCancelled } from "./meetingResponse"
import { RequestJsonFunction } from "./types";

interface GetMeetingFunction {
  (id: string | undefined): Promise<Meeting>
}

export function buildGetMeeting(requestJson: RequestJsonFunction): GetMeetingFunction {
  async function getMeeting(id: string | undefined): Promise<Meeting> {
    if (id === undefined) {
      throw new Error("Meeting id is undefined")
    }

    const url: URL = new URL(`${BASE_URL}/getMeeting`)
    url.searchParams.append("id", id)

    const json: Promise<any> = await requestJson(url)
    if (!isMeetingResponse(json)) {
      throw new Error("not a meeting response")
    } 

    const resp: MeetingResponse = json
    const meetingDoc: MeetingDocument<boolean> = resp.meeting
    const basicMeetingInfo =  {
      id: meetingDoc.id,
      body: meetingDoc.body,
      meetingDate: new Date(meetingDoc.meeting_dt * 1000),
      filingDate: new Date(meetingDoc.filing_dt * 1000),
      address: meetingDoc.address,
      is_emergency: meetingDoc.is_emergency,
      is_annual_calendar: meetingDoc.is_annual_calendar,
      is_public_notice: meetingDoc.is_public_notice,
      latestAgenda: meetingDoc.latestAgenda,
      latestAgendaLink: meetingDoc.latestAgendaLink, 
      latestMinutes: meetingDoc.latestMinutes, 
      latestMinutesLink: meetingDoc.latestMinutesLink,
      contactPerson: meetingDoc.contactPerson,
      contactEmail: meetingDoc.contactEmail,
      contactPhone: meetingDoc.contactPhone,
    }

    if (isCancelled(meetingDoc)) {
      return {
        isCancelled: true,
        cancelledDate: new Date(meetingDoc.cancelled_dt * 1000),
        cancelledReason: meetingDoc.cancelled_reason,
        ...basicMeetingInfo,
       }
    } else {
      return {
        isCancelled: false,
        ...basicMeetingInfo
       }
    }
  }
  return getMeeting
}