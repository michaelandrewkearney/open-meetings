import Typesense, { Client } from "typesense";
import { CollectionSchema } from "typesense/lib/Typesense/Collection";
import { CollectionCreateSchema } from "typesense/lib/Typesense/Collections";
import { ImportResponse } from "typesense/lib/Typesense/Documents";
import { Meeting, getMeetingData } from "./meeting_data";

const API_KEY = process.env.TYPESENSE_API_KEY!
const TIMEOUT_MINUTES = 5

const port = process.argv[2]
const confirm = process.argv[3]

let client: Client = new Typesense.Client({
  'nodes': [{
    'host': 'localhost',
    'port': parseInt(port),      
    'protocol': 'http' 
  }],
  'apiKey': API_KEY,
  'connectionTimeoutSeconds': TIMEOUT_MINUTES * 60
})

async function deleteCollections() {
  const existingCollections = await client.collections().retrieve()
  // delete all current collections
  if (existingCollections.length > 0) {
    console.log("deleting old collections...")
  }
  existingCollections.forEach(async (schema) => {
    await client.collections(schema.name).delete()
    console.log(`deleted ${schema.name} collection`)
  }
  )
}

if (confirm == 'confirm') {
  deleteCollections()
} else {
  console.log('Must pass port number and CONFIRM as arguments to clear documents. No documents were cleared.')
}
