import { BASE_URL } from "../../config";
import { SearchResponse } from "../../server/searchResponse";
import { mockMeetingMetadata } from "./meetingMetadata";

export const apiResponses: Map<string, SearchResponse> = new Map()

// BASE_URL can be modified in src/config.ts
const searchURL: URL = new URL(`${BASE_URL}/searchMeeting`)

const allMeetingsParams= new URLSearchParams([
  ["keyphrase", "*"],
])
apiResponses.set(`${searchURL}?${allMeetingsParams}`, {
  result: "success",
  found: 4, 
  out_of: 4, 
  page: 1,
  facet_counts: [
    {
      counts: [
        {
          count: 2,
          value: "Rhode Island School Building Taskforce",
        },
        {
          count: 2,
          value: "Barrington School Committee",
        },
      ],
      field_name: "body"
    },
  ],
  hits: [
    {
      highlights: [],
      document: mockMeetingMetadata.get("1")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("2")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("3")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("4")!
    }
  ]
})

const taskforceBodySearchParams = new URLSearchParams([
  ["keyphrase", "*"],
  ["publicBody", "Rhode Island School Building Taskforce"]
])
apiResponses.set(`${searchURL}?${taskforceBodySearchParams}`, {
  result: "success",
  found: 2, 
  out_of: 4, 
  page: 1,
  facet_counts: [
    {
      counts: [
        {
          count: 2,
          value: "Rhode Island School Building Taskforce",
        },
      ],
      field_name: "body"
    },
  ],
  hits: [
    {
      highlights: [],
      document: mockMeetingMetadata.get("1")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("2")!
    },
  ]
})

const barringtonBodySearchParams = new URLSearchParams([
  ["keyphrase", "*"],
  ["publicBody", "Barrington School Committee"]
])
apiResponses.set(`${searchURL}?${barringtonBodySearchParams}`, {
  result: "success",
  found: 2, 
  out_of: 4, 
  page: 1,
  facet_counts: [
    {
      counts: [
        {
          count: 2,
          value: "Barrington School Committee",
        },
      ],
      field_name: "body"
    },
  ],
  hits: [
    {
      highlights: [],
      document: mockMeetingMetadata.get("3")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("4")!
    },
  ]
})

const startDateSearchParams = new URLSearchParams([
  ["keyphrase", "*"],
  ["dateStart", (new Date(2022, 4 - 1, 1).getTime() / 1000).toString()],
])
apiResponses.set(`${searchURL}?${startDateSearchParams}`, {
  result: "success",
  found: 3, 
  out_of: 4, 
  page: 1,
  facet_counts: [
    {
      counts: [
        {
          count: 2,
          value: "Rhode Island School Building Taskforce",
        },
        {
          count: 1,
          value: "Barrington School Committee",
        },
      ],
      field_name: "body"
    },
  ],
  hits: [
    {
      highlights: [],
      document: mockMeetingMetadata.get("1")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("2")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("4")!
    }
  ]
})

const bothDateSearchParams = new URLSearchParams([
  ["keyphrase", "*"],
  ["dateStart", (new Date(2022, 4 - 1, 1).getTime() / 1000).toString()],
  ["dateEnd", (new Date(2023, 3 - 1, 15).getTime() / 1000).toString()],
])
apiResponses.set(`${searchURL}?${bothDateSearchParams}`, {
  result: "success",
  found: 3, 
  out_of: 4, 
  page: 1,
  facet_counts: [
    {
      counts: [
        {
          count: 1,
          value: "Rhode Island School Building Taskforce",
        },
        {
          count: 2,
          value: "Barrington School Committee",
        },
      ],
      field_name: "body"
    },
  ],
  hits: [
    {
      highlights: [],
      document: mockMeetingMetadata.get("2")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("3")!
    },
    {
      highlights: [],
      document: mockMeetingMetadata.get("4")!
    }
  ]
})