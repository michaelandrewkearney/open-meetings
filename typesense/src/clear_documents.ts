import Typesense, { Client } from "typesense";
import { CollectionSchema } from "typesense/lib/Typesense/Collection";
import ObjectNotFound from "typesense/lib/Typesense/Errors/ObjectNotFound";

const API_KEY = process.env.TYPESENSE_API_KEY!
const TIMEOUT_MINUTES = 5

const collection = process.argv[2]
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

async function deleteCollections(collection: string) {
  try {
    const collectionSchema = await client.collections(collection).retrieve()
    let deleted: CollectionSchema = await client.collections(collectionSchema.name).delete()
    console.log(`Deleted ${deleted.name} collection.`)
  } catch (e) {
    if (e instanceof ObjectNotFound) {
      console.log(`Could not find collection named ${collection}.`)
    }
  }
}

deleteCollections(collection)
