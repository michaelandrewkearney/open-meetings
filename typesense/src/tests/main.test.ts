import Typesense, { Client } from "typesense";
import { Meeting, isRawMeeting, getMeetingData } from "../meeting_data";
import mockMeetingJson from "../../data/test_omp_data.json"
import { SearchResponse } from "typesense/lib/Typesense/Documents";


const client = new Typesense.Client({
  'nodes': [{
    'host': 'localhost',
    'port': 1818,      
    'protocol': 'http' 
  }],
  'apiKey': process.env.TYPESENSE_API_KEY!,
  'connectionTimeoutSeconds': 60
})

test("is_a_meeting", function() {
  const meetingsJson = require('../../data/test_omp_data.json')
  meetingsJson.forEach((obj: any) => {
    expect(isRawMeeting(obj)).toBeTruthy()
  })
})

test('retrieve a meeting by id', async function() {
  const meeting = await client.collections<Meeting>('meetings')
    .documents('1042582')
    .retrieve()
  expect(meeting.id).toBe(mockMeetingJson[0].id)
  expect(meeting.body).toBe(mockMeetingJson[0].body)
});

test('first search!!', async function() {
  let searchParameters = {
    'q'         : 'collective',
    'query_by'  : 'latestAgenda',
  }
  const resp = await client.collections('meetings')
  .documents()
  .search(searchParameters)

  const firstHit = resp.hits![0]
});

test('faceted search!!', async function() {
  let searchParameters = {
    'q'         : 'the',
    'query_by'  : 'latestAgenda',
    'facet_by' : "body"
  }
  const resp = await client.collections('meetings')
  .documents()
  .search(searchParameters)

  console.log((resp.facet_counts![0]).counts)
});