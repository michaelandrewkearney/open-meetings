import { BASE_URL } from "../../config";
import { MeetingResponse } from "../../server/meetingResponse";
import { SearchResponse } from "../../server/searchResponse";
import { mockMeetingMetadata } from "./meetingMetadata";
import { mockMeetings } from "./mockMeetings";

export const apiResponses: Map<string, SearchResponse|MeetingResponse> = new Map()

// BASE_URL can be modified in src/config.ts
const searchURL: URL = new URL(`${BASE_URL}/searchMeeting`)
const getMeetingURL: URL = new URL(`${BASE_URL}/getMeeting`)

const allMeetingsParams= new URLSearchParams([
  ["keyphrase", "*"],
])
apiResponses.set(`${searchURL}?${allMeetingsParams}`, {
  response_type: "success",
  found: 4, 
  out_of: 4, 
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
      fieldName: "body"
    },
  ],
  hits: [
    {
      document: mockMeetings.get("1")!,
      highlight: {},
      text_match: 0
    },
  ]
})

// const taskforceBodySearchParams = new URLSearchParams([
//   ["keyphrase", "*"],
//   ["publicBody", "Rhode Island School Building Taskforce"]
// ])
// apiResponses.set(`${searchURL}?${taskforceBodySearchParams}`, {
//   result: "success",
//   found: 2, 
//   out_of: 4, 
//   facet_counts: [
//     {
//       counts: [
//         {
//           count: 2,
//           value: "Rhode Island School Building Taskforce",
//         },
//       ],
//       fieldName: "body"
//     },
//   ],
//   hits: [
//     {
//       highlights: [{
//         snippet
//       }],
//       document: mockMeetingMetadata.get("1")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("2")!
//     },
//   ]
// })

// const barringtonBodySearchParams = new URLSearchParams([
//   ["keyphrase", "*"],
//   ["publicBody", "Barrington School Committee"]
// ])
// apiResponses.set(`${searchURL}?${barringtonBodySearchParams}`, {
//   result: "success",
//   found: 2, 
//   out_of: 4, 
//   facet_counts: [
//     {
//       counts: [
//         {
//           count: 2,
//           value: "Barrington School Committee",
//         },
//       ],
//       fieldName: "body"
//     },
//   ],
//   hits: [
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("3")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("4")!
//     },
//   ]
// })

// const startDateSearchParams = new URLSearchParams([
//   ["keyphrase", "*"],
//   ["dateStart", (new Date(2022, 4 - 1, 1).getTime() / 1000).toString()],
// ])
// apiResponses.set(`${searchURL}?${startDateSearchParams}`, {
//   result: "success",
//   found: 3, 
//   out_of: 4, 
//   facet_counts: [
//     {
//       counts: [
//         {
//           count: 2,
//           value: "Rhode Island School Building Taskforce",
//         },
//         {
//           count: 1,
//           value: "Barrington School Committee",
//         },
//       ],
//       field_name: "body"
//     },
//   ],
//   hits: [
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("1")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("2")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("4")!
//     }
//   ]
// })

// const bothDateSearchParams = new URLSearchParams([
//   ["keyphrase", "*"],
//   ["dateStart", (new Date(2022, 4 - 1, 1).getTime() / 1000).toString()],
//   ["dateEnd", (new Date(2023, 3 - 1, 15).getTime() / 1000).toString()],
// ])
// apiResponses.set(`${searchURL}?${bothDateSearchParams}`, {
//   result: "success",
//   found: 3, 
//   out_of: 4, 
//   facet_counts: [
//     {
//       counts: [
//         {
//           count: 1,
//           value: "Rhode Island School Building Taskforce",
//         },
//         {
//           count: 2,
//           value: "Barrington School Committee",
//         },
//       ],
//       field_name: "body"
//     },
//   ],
//   hits: [
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("2")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("3")!
//     },
//     {
//       highlights: [],
//       document: mockMeetingMetadata.get("4")!
//     }
//   ]
// })

// const taskforceKeywordSearchParams = new URLSearchParams([
//   ["keyphrase", "taskforce"],
// ])
// apiResponses.set(`${searchURL}?${taskforceKeywordSearchParams}`, {
//   result: "success",
//   found: 4, 
//   out_of: 4, 
//   facet_counts: [
//     {
//       counts: [
//         {
//           count: 2,
//           value: "Rhode Island School Building Taskforce",
//         },
//         {
//           count: 2,
//           value: "Barrington School Committee",
//         },
//       ],
//       field_name: "body"
//     },
//   ],
//   hits: [
//     {
//       highlights: [
//         {
//           field: "body",
//           snippet: "Rhode Island School Building <mark>Taskforce</mark>",
//           matched_tokens: [],
//         },
//         {
//           field: "latestMinutes",
//           snippet: "the <mark>taskforce</mark>'s primary goals are to create a working group",
//           matched_tokens: ["taskforce"],
//         }
//       ],
//       document: mockMeetingMetadata.get("1")!
//     },
//     {
//       highlights: [
//         {
//           field: "body",
//           snippet: "Rhode Island School Building <mark>Taskforce</mark>"
//         },
//       ],
//       document: mockMeetingMetadata.get("2")!
//     },
//     {
//       highlights: [
//         {
//           field: "latestMinutes",
//           snippet: "the <mark>taskforce</mark> has made progress along several front, the <mark>taskforce</mark>"
//         }
//       ],
//       document: mockMeetingMetadata.get("3")!
//     },
//     {
//       highlights: [        
//         {
//         field: "latestAgenda",
//         snippet: "vote to create new <mark>taskforce</mark> for school lunches"
//       }],
//       document: mockMeetingMetadata.get("4")!
//     }
//   ]
// })


// apiResponses.set(`${getMeetingURL}?id=1`, {
//   result: "success",
//   meeting: mockMeetings.get("1")!
// })