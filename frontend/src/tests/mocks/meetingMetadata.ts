import { MeetingDocumentMetadata } from "../../server/searchResponse"

export const mockMeetingMetadata: Map<string, MeetingDocumentMetadata<boolean>> = new Map()

mockMeetingMetadata.set("1", {
  id: "1",
  body: "Rhode Island School Building Taskforce",
  meeting_dt: new Date(2023, 4 - 1, 10).getTime() / 1000,
  address: "East Providence High School - library, 2000 Pawtucket Avenue, East Providence, RI, 02914",
  is_cancelled: false,
  cancelled_dt: null
})

mockMeetingMetadata.set("2", {
  id: "2",
  body: "Rhode Island School Building Taskforce",
  meeting_dt: new Date(2023, 3 - 1, 15).getTime() / 1000, // 3/15/2023
  address: "East Providence High School - library, 2000 Pawtucket Avenue, East Providence, RI, 02914",
  is_cancelled: true,
  cancelled_dt: new Date(2023, 3 - 1, 10).getTime() / 1000,
})

mockMeetingMetadata.set("3", {
  id: "3",
  body: "Barrington School Committee",
  meeting_dt: new Date(2022, 3 - 1, 18).getTime() / 1000,
  address: "Barrington Middle School, 261 Middle Highway, Barrington, RI, 02806",
  is_cancelled: false,
  cancelled_dt: null,
})

mockMeetingMetadata.set("4", {
  id: "4",
  body: "Barrington School Committee",
  meeting_dt: new Date(2023, 2 - 1, 18).getTime() / 1000,
  address: "Barrington Middle School, 261 Middle Highway, Barrington, RI, 02806",
  is_cancelled: false,
  cancelled_dt: null,
})