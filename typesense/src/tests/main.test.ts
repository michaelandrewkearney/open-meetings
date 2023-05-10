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

test('meeting collection exists', async function() {
  const collections = await client.collections().retrieve()
  expect(collections.find(collection => collection.name === "meetings")).toBeTruthy()
});

test('five documents are indexed', async function() {
  const meetingCollection = await client.collections('meetings').retrieve()
  expect(meetingCollection.num_documents).toBe(5)
});

test('retrieve a meeting by id', async function() {
  const meeting = await client.collections<Meeting>('meetings')
    .documents('1042582')
    .retrieve()
  expect(meeting.id).toBe(mockMeetingJson[0].id)
  expect(meeting.body).toBe(mockMeetingJson[0].body)
});

test('first search', async function() {
  let searchParameters = {
    'q'         : 'collective',
    'query_by'  : 'latestAgenda',
  }
  const resp: SearchResponse<{}> = await client.collections('meetings')
  .documents()
  .search(searchParameters)

  expect(resp.found).toBe(1)
  expect(resp.out_of).toBe(5)
});

