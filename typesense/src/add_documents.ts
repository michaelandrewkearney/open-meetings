import Typesense, { Client } from "typesense";
import { CollectionSchema } from "typesense/lib/Typesense/Collection";
import { CollectionCreateSchema } from "typesense/lib/Typesense/Collections";
import { ImportResponse } from "typesense/lib/Typesense/Documents";
import { Meeting, getMeetingData } from "./meeting_data";

const API_KEY = process.env.TYPESENSE_API_KEY!
const TIMEOUT_MINUTES = 5

const meetingsJsonPath = process.argv[2]
const port = process.argv[3]

let client: Client = new Typesense.Client({
  'nodes': [{
    'host': 'localhost',
    'port': parseInt(port),      
    'protocol': 'http' 
  }],
  'apiKey': API_KEY,
  'connectionTimeoutSeconds': TIMEOUT_MINUTES * 60
})

async function importMeetingsFromJSON(): Promise<ImportResponse[]> {
  const meetingsJson = require(meetingsJsonPath)
  const meetings: Meeting[] = getMeetingData(meetingsJson)
  return client.collections('meetings')
    .documents()
    .import(meetings, {action: 'create'})
}

async function createMeetingsCollection(): Promise<CollectionSchema> {
  const existingCollections = await client.collections().retrieve()
  const maybeMeetingsCollection = existingCollections.find((schema) =>
    schema.name === "meetings"
  )
  // if meetings collection already exists, delete it
  if (maybeMeetingsCollection) {
    console.log("deleting old meetings collection")
    client.collections('meetings').delete()
  }
  let schema: CollectionCreateSchema = {
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
      },
      {
        name: "contactEmail",
        type: "string",
        facet: false,
      },
      {
        name: "contactPhone",
        type: "string",
        facet: false,
      },
    ]
  }
  return client.collections().create(schema)
}

async function indexMeetings() {
  console.log("creating meetings collections...")
  await createMeetingsCollection()
  console.log("meetings collection successfully created")

  console.log(`importing meetings from ${meetingsJsonPath}`)
  const importResults: ImportResponse[] = await importMeetingsFromJSON()
  let totalImports: number = 0 
      
  importResults.forEach((resp: ImportResponse) => {
    if (!resp.success) {
      console.log("Error importing meetings")
      console.log(resp)
    }
    totalImports += 1
  })

  const successfulImports = (await client.collections('meetings').retrieve()).num_documents

  console.log("meeting import finished")
  console.log(`successfully imported ${successfulImports} out of ${totalImports} meetings`)
}

indexMeetings()