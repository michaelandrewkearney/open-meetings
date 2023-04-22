import { BASE_URL } from "../config";
import { CancelledMeetingResult, MeetingResult, PlannedMeetingResult, Search, SearchState } from "../meetingTypes";
import { Facet, Hit, MeetingDocumentMetadata, SearchResponse, isCancelled, isSearchResponse } from "./searchResponse";
import { RequestJsonFunction } from "./types";

interface SearchEndpointParams {
  keyphrase: string, 
  page?: number,
  per_page?: number, 
  publicBody?: string, 
  dateStart?: number,
  dateEnd?: number,
}

interface SearchFunction {
  (keyphrase: string, selectedBody: string | null, dateStart: Date | null,  dateEnd: Date | null): Promise<Search>
}

/**
 * Returns search function given a RequestJsonFunction to fetch the json 
 * response. Allows for using mock API reponses. 
 * 
 * @param requestJson 
 * @returns 
 */
export function buildSearch(requestJson: RequestJsonFunction): SearchFunction {
  async function search(
    keyphrase: string, 
    body: string | null,
    dateStart: Date | null, 
    dateEnd: Date | null): Promise<Search> {

    const searchParams: SearchEndpointParams = {
      // Typesense wants query="*" to return all documents
      keyphrase: keyphrase === "" ? "*" : keyphrase,
      publicBody: body ? body : undefined,
      dateStart: dateStart ? dateStart.getTime() / 1000 : undefined,
      dateEnd: dateEnd ? dateEnd.getTime() / 1000 : undefined
    }
    const fetchResponse = buildGetSearchResponse(requestJson)
    const resp: SearchResponse = await fetchResponse(searchParams)

    //Map of public body names to counts
    const bodyFacetMap: Map<string, number> = new Map()
    const bodyFacet: Facet | undefined = resp.facet_counts.find((facet) => facet.field_name === "body")
    
    if (bodyFacet === undefined) {
      throw new Error("body facet not in search response")
    }
    bodyFacet.counts.forEach((facetCount) => {
      bodyFacetMap.set(facetCount.value, facetCount.count)
    })

    // return new Search
    return {
      keyphrase: keyphrase,
      bodyFacetMap: bodyFacetMap,
      resultsInfo: {found: resp.found, outOf: resp.out_of},
      selectedBody: null,
      results: convertHits(resp.hits)
    }
  }
  return search;
}

/**
 * Converts Hits from the API response to custom MeetingResult objects used
 * in the React app.
 * 
 * @param hits 
 * @returns 
 */
function convertHits(hits: Hit[]): MeetingResult[] {
  const results: MeetingResult[] = []
  hits.forEach((hit: Hit) => {
    const doc: MeetingDocumentMetadata<boolean> = hit.document
    const basicMeetingInfo = {
      id: doc.id,
      body: doc.body,
      meetingDate: new Date(doc.meeting_dt * 1000),
      address: doc.address,
      highlights: hit.highlights,
    }
    if (isCancelled(doc)) {
      const meetingResult: CancelledMeetingResult = {
        ...basicMeetingInfo,
        isCancelled: true,
        cancelledDate: new Date(doc.cancelled_dt * 1000)
      }
      results.push(meetingResult)
    } else {
      const meetingResult: PlannedMeetingResult = {
        ...basicMeetingInfo,
        isCancelled: false,
      }
      results.push(meetingResult) 
    }
  })
  return results
}


/**
 * Function that gets search response from API meetingSearch endpoint
 */
interface GetSearchResponseFunction {
  (params: SearchEndpointParams): Promise<SearchResponse>
}

/**
 * Returns getSearchResponse function given a RequestJsonFunction to fetch the json 
 * response. Allows for using mock API reponses. 
 * @param requestJson 
 * @returns 
 */
function buildGetSearchResponse(requestJson: RequestJsonFunction): GetSearchResponseFunction {
    async function getSearchResponse({ keyphrase, page, per_page, publicBody, dateStart, dateEnd }: SearchEndpointParams): Promise<SearchResponse> {

    const url: URL = new URL(`${BASE_URL}/searchMeeting`)
    url.searchParams.append("keyphrase", keyphrase)

    if (publicBody) url.searchParams.append("publicBody", publicBody)
    if (dateStart) url.searchParams.append("dateStart", dateStart.toString())
    if (dateEnd) url.searchParams.append("dateEnd", dateEnd.toString())
    
    const json: Promise<any> = await requestJson(url)
    if (isSearchResponse(json)) {
      const resp: SearchResponse = json
      return resp;
    } else {
      throw new Error("not a search response")
    }
  }
  return getSearchResponse
}