import Typesense, { Client } from "typesense";
import { CollectionSchema } from "typesense/lib/Typesense/Collection";
import { CollectionCreateSchema } from "typesense/lib/Typesense/Collections";
import { ImportResponse } from "typesense/lib/Typesense/Documents";
import { Meeting, getMeetingData } from "./meeting_data";

const API_KEY = process.env.TYPESENSE_API_KEY!
const TIMEOUT_MINUTES = 5

const port = process.argv[2]
const meetingsJsonPath = process.argv[3]

const meetings_schema: CollectionCreateSchema = {
  name: "meetings", 
  fields: [
    {
      name: "body",
      type: "string",
      facet: true
    },
    {
      name: "meeting_dt",
      type: "int64",
      facet: true
    },
    {
      name: "address",
      type: "string",
      facet: false,
    },
    {
      name: "filing_dt",
      type: "int64",
      facet: false,
    },
    {
      name: "is_emergency",
      type: "bool",
      facet: false,
    },
    {
      name: "is_annual_calendar",
      type: "bool",
      facet: false,
    },
    {
      name: "is_public_notice",
      type: "bool",
      facet: false,
    },
    {
      name: "is_cancelled",
      type: "bool",
      facet: false,
    },
    {
      name: "cancelled_dt",
      type: "int64",
      facet: false,
      optional: true,
    },
    {
      name: "cancelled_reason",
      type: "string",
      facet: false,
      optional: true,
    },
    {
      name: "latestAgenda",
      type: "string[]",
      facet: false,
      optional: true,
    },
    {
      name: "latestAgendaLink",
      type: "string",
      facet: false,
      optional: true,
    },
    {
      name: "latestMinutes",
      type: "string[]",
      facet: false,
      optional: true,
    },
    {
      name: "latestMinutesLink",
      type: "string",
      facet: false,
      optional: true,
    },
    {
      name: "contactPerson",
      type: "string",
      facet: false,
      optional: true
    },
    {
      name: "contactEmail",
      type: "string",
      facet: false,
      optional: true
    },
    {
      name: "contactPhone",
      type: "string",
      facet: false,
      optional: true
    }
  ]
}

let client: Client = new Typesense.Client({
  'nodes': [{
    'host': 'localhost',
    'port': parseInt(port),      
    'protocol': 'http' 
  }],
  'apiKey': API_KEY,
  'connectionTimeoutSeconds': TIMEOUT_MINUTES * 60
})

async function importMeetingsFromJSON(path: string): Promise<ImportResponse[]> {
  const meetingsJson = require(path)
  const meetings: Meeting[] = getMeetingData(meetingsJson)
  return client.collections(meetings_schema.name)
    .documents()
    .import(meetings, {action: 'create'})
}

async function getOrCreateMeetingsCollection(): Promise<CollectionSchema> {
  const meetingsCollectionSchema: CollectionSchema = await client.collections(meetings_schema.name).retrieve()

  if (meetings_schema.name in meetingsCollectionSchema){
    return meetingsCollectionSchema
  }
  return client.collections().create(meetings_schema)
}

async function indexMeetings() {
  console.log("creating meetings collections...")
  await getOrCreateMeetingsCollection()
  console.log("meetings collection successfully created")

  console.log(`importing meetings from ${meetingsJsonPath}`)
  const importResults: ImportResponse[] = await importMeetingsFromJSON(meetingsJsonPath)
  let total_imports: number = importResults.length
  let failures: number = 0
      
  importResults.forEach((resp: ImportResponse) => {
    if (!resp.success) {
      console.log("Error importing meetings")
      console.log(resp)
      failures += 1
    }
  })

  const total_doc_count: number = (await client.collections('meetings').retrieve()).num_documents

  console.log("meeting import finished")
  console.log(`successfully imported ${total_imports-failures} out of ${total_imports} meetings. total document count is now ${total_doc_count}`)
}

indexMeetings()