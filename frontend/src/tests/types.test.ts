import "@testing-library/jest-dom";
import { isMeeting, Meeting } from "../meetingTypes";
import { isMeetingResponse, isCancelled } from "../server/meetingResponse";
import { isSearchResponse } from "../server/searchResponse";

test("isMeeting correctness", () => {
  let startMeeting: any = {
    id: "a",
    body: "a",
    meetingDate: "a",
    address: "as",
    latestAgenda: null,
    latestAgendaLink: null,
    latestMinutes: null,
    latestMinutesLink: null,
    contactPerson: "as",
    contactEmail: "ah",
  };

  // valid meetings
  let abstractMeeting: any = { ...startMeeting, contactPhone: "123" };
  let plannedMeeting: any = { ...abstractMeeting, isCancelled: false };
  let cancelledMeeting: any = {
    ...abstractMeeting,
    isCancelled: true,
    cancelledDate: "as",
    cancelledReason: "ah",
  };

  // not valid meetings
  let notPlanned: any = { ...startMeeting, isCancelled: false };
  let notPlanned2: any = { ...abstractMeeting, isCancelled: true };
  let notCancelled: any = {
    ...startMeeting,
    isCancelled: true,
    cancelledData: "as",
    cancelledReason: "ah",
  };
  let notCancelled2: any = {
    ...abstractMeeting,
    isCancelled: false,
    cancelledData: "as",
    cancelledReason: "ah",
  };

  // test valid meetings
  expect(isMeeting(plannedMeeting)).toBeTruthy();
  expect(isMeeting(cancelledMeeting)).toBeTruthy();

  // test invalid cases
  expect(!isMeeting(startMeeting));
  expect(!isMeeting(abstractMeeting));
  expect(!isMeeting(notPlanned));
  expect(!isMeeting(notPlanned2));
  expect(!isMeeting(notCancelled));
  expect(!isMeeting(notCancelled2));
});

test("isMeetingResponse correctness", () => {
  let meetingDoc = {
    id: "ah",
    body: "as",
    meeting_dt: "as",
    address: "as",
    is_cancelled: false,
    cancelled_dt: null,
    cancelled_reason: null,
    latestAgenda: null,
    latestAgendaLink: null,
    latestMinutes: null,
    latestMinutesLink: null,
    contactPerson: "a",
    contactEmail: "a",
    contactPhone: "a",
  };

  let response: any = {
    result: "success",
    meeting: meetingDoc,
  };

  // invalid response
  let notResponse: any = {
    result: "a",
    meeting: meetingDoc,
  };

  let notResponse2: any = {
    result: "a",
  };

  // test isMeetingResponse
  expect(isMeetingResponse(response)).toBeTruthy();
  expect(!isMeetingResponse(notResponse)).toBeTruthy();
  expect(!isMeetingResponse(notResponse2)).toBeTruthy();
});

test("isSearchResponse correctness", () => {
  let searchResponseStart = {
    result: "success",
    found: 1,
    out_of: 2,
    page: 3,
  };

  let f1: any = { counts: [{ count: 1, value: "as" }], field_name: "boo" };

  let docData = {
    id: "ah",
    body: "as",
    meeting_dt: "as",
    address: "as",
    is_cancelled: false,
    cancelled_dt: null,
  };

  let h1: any = {
    highlights: [{ field: 1, snippet: "as" }],
    document: docData,
  };

  let sresponse = {
    ...searchResponseStart,
    facet_counts: [f1],
    hits: [h1],
  };

  // invalid search response
  let notResponse = { ...searchResponseStart, facet_counts: 1, hits: 2 };
  let notResponse2 = { ...searchResponseStart, facet_counts: [f1], hits: 2 };
  let notResponse3 = { ...searchResponseStart, facet_counts: 1, hits: [h1] };

  // test isSearchResponse
  expect(isSearchResponse(sresponse)).toBeTruthy();
  expect(!isSearchResponse(searchResponseStart)).toBeTruthy();
  expect(!isSearchResponse(notResponse)).toBeTruthy();
  expect(!isSearchResponse(notResponse2)).toBeTruthy();
  expect(!isSearchResponse(notResponse3)).toBeTruthy();
});
