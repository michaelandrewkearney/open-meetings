import { apiResponses } from "./apiResponses";

export default function mockRequestJson(url: URL): any {
  console.log(url.href)
  const json = apiResponses.get(url.href)
  console.log(json)
  console.log([...apiResponses.keys()])
  return Promise.resolve(json)
}