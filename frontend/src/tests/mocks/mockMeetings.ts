import { MeetingDocument } from "../../server/meetingResponse";

export const mockMeetings: Map<string, MeetingDocument<boolean>> = new Map()

mockMeetings.set("1", {
  id: "1",
  body: "Rhode Island School Building Taskforce",
  meeting_dt: new Date(2023, 4 - 1, 10).getTime() / 1000,
  filing_dt: new Date(2023, 4 - 1, 2).getTime() / 1000,
  address: "East Providence High School - library, 2000 Pawtucket Avenue, East Providence, RI, 02914",
  is_cancelled: false,
  cancelled_dt: null,
  cancelled_reason: null,
  is_annual_calendar: true, 
  is_emergency: false, 
  is_public_notice: false,
  latestAgenda: ["on the agenda is the following:", "discussing the taskforce", "the budget for the taskforce"], 
  latestAgendaLink: "https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4692%5C2023%5C457017.pdf",
  latestMinutes: ["today we are coming to gather a taskforce", "the taskforce has made progress along several front, the taskforce along several fronts including:", "improving bathroom facilities"],
  latestMinutesLink: "https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4495%5C2023%5C458152.pdf",
  contactPerson: "taskforce person",
  contactEmail: "taskforce@gmail.com",
  contactPhone: "(888)-888-8888"
})
