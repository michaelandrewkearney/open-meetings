import Typesense, { Client } from "typesense";
import { CollectionSchema } from "typesense/lib/Typesense/Collection";
import { CollectionCreateSchema } from "typesense/lib/Typesense/Collections";
import { ImportResponse } from "typesense/lib/Typesense/Documents";
import { Meeting, getMeetingData } from "./meeting_data";
import { ObjectNotFound } from "typesense/lib/Typesense/Errors";

const API_KEY = process.env.TYPESENSE_API_KEY!
const TIMEOUT_MINUTES = 5

const meetingsJsonPath = process.argv[2]
const port = process.argv[3]

const meetingsCreateSchema: CollectionCreateSchema = {
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

async function indexFromJson(collection: string, path: string, jsonToArray: Function): Promise<ImportResponse[]> {
  const json = require(path)
  const documents: any[] = jsonToArray(json)
  return client.collections(collection)
    .documents()
    .import(documents, {action: 'create'})
}

async function createCollectionIfNotExists(schema: CollectionCreateSchema): Promise<boolean> {
  try {
    const existingSchema: CollectionSchema = await client.collections(schema.name).retrieve()
    return false
  } catch (e) {
    if (e instanceof ObjectNotFound) {
      await client.collections().create(schema)
      return true
    } else {
      throw e
    }
  }
}

async function indexMeetings() {
  console.log("Checking for meetings collections...")
  let created: Promise<boolean> = createCollectionIfNotExists(meetingsCreateSchema)
  created.then((val) => {
    if (val) {
      console.log("Created meetings collection.")
    } else {
      console.log("Meetings collection already created.")
    }
  })

  console.log(`Importing meetings from ${meetingsJsonPath}`)
  const importResults: ImportResponse[] = await indexFromJson(meetingsCreateSchema.name, meetingsJsonPath, getMeetingData)

  let failures: number = 0
  importResults.forEach((resp: ImportResponse) => {
    if (!resp.success) {
      console.log("Error importing meeting:")
      console.log(resp)
      failures += 1
    }
  })

  const total_doc_count: number = (await client.collections(meetingsCreateSchema.name).retrieve()).num_documents

  console.log(`Imported ${importResults.length-failures} out of ${importResults.length} meetings. Total document count is now ${total_doc_count}.`)
}

indexMeetings()