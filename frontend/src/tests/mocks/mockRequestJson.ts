import { apiResponses } from "./mockAPI";

export default function mockRequestJson(url: URL): any {
  console.log(url.href)
  console.log([...apiResponses.keys()])
  const json = apiResponses.get(url.href)
  console.log(json)

  return Promise.resolve(json)
}