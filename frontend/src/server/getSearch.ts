import { SearchResponseFacetCountSchema, SearchResponseHit } from "typesense/lib/Typesense/Documents";
import { BASE_URL } from "../config";
import { CancelledMeetingResult, MeetingResult, PlannedMeetingResult, ResultHighlight, SearchFilters, SearchResults } from "../meetingTypes";
import { FacetCount, Hit, MeetingDocumentMetadata, SearchResponse, isCancelled, isSearchResponse } from "./searchResponse";
import { RequestJsonFunction } from "./types";
import { MeetingDocument } from "./meetingResponse";
import { DocumentHighlights } from "typescript";

interface SearchEndpointParams {
  keyphrase: string, 
  page?: number,
  per_page?: number, 
  publicBody?: string, 
  dateStart?: number,
  dateEnd?: number,
}

interface SearchFunction {
  (keyphrase: string, filters: SearchFilters): Promise<SearchResults>
}

/**
 * Returns search function given a RequestJsonFunction to fetch the json 
 * response. Allows for using mock API reponses. 
 * 
 * @param requestJson 
 * @returns 
 */
export function buildSearch(requestJson: RequestJsonFunction): SearchFunction {
  async function search(keyphrase: string, filters: SearchFilters): Promise<SearchResults> {
    const {body, dateStart, dateEnd} = filters
    const searchParams: SearchEndpointParams = {
      // Typesense wants query="*" to return all documents
      keyphrase: keyphrase,
      publicBody: body ? body : undefined,
      dateStart: dateStart ? dateStart.getTime() / 1000 : undefined,
      dateEnd: dateEnd ? dateEnd.getTime() / 1000 : undefined
    }
    const fetchResponse = buildGetSearchResponse(requestJson)
    const resp: SearchResponse = await fetchResponse(searchParams)

    //Map of public body names to counts
    const bodyFacetMap: Map<string, number> = new Map()
    const bodyFacet: FacetCount | undefined = resp.facet_counts.find((facet) => facet.fieldName === "body")
    
    if (bodyFacet === undefined) {
      throw new Error("body facet not in search response")
    }
    bodyFacet.counts.forEach((facetCount: { value: string; count: number; }) => {
      bodyFacetMap.set(facetCount.value, facetCount.count)
    })

    // return new Search
    return {
      bodyFacetMap: bodyFacetMap,
      resultsInfo: {found: resp.found, outOf: resp.out_of},
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
    const doc: MeetingDocument<boolean> = hit.document
    const basicMeetingInfo = {
      id: doc.id,
      body: doc.body,
      meetingDate: new Date(doc.meeting_dt * 1000),
      address: doc.address,
      highlights: convertHighlights(hit),
      latestAgendaPreview: doc.latestAgenda?.at(0),
      filing_dt: doc.filing_dt,
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


function convertHighlights(hit: Hit): ResultHighlight[] | undefined {
  const highlights = hit.highlights
  if (!highlights) {return undefined}

  let toReturn: ResultHighlight[] = [];
  highlights.forEach(highlight => {
    if ("snippets" in highlight) {
      toReturn.push({
        field: highlight.field,
        snippets: highlight.snippets!
      })
    } else {
      toReturn.push({
        field: highlight.field,
        snippet: highlight.snippet!
      })
    }
  })

  return toReturn
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
    async function getSearchResponse({ keyphrase, publicBody, dateStart, dateEnd }: SearchEndpointParams): Promise<SearchResponse> {

    console.log("in getsearch response")
    console.log({ keyphrase, publicBody, dateStart, dateEnd })

    const url: URL = new URL(`${BASE_URL}/meetingSearch`)
    url.searchParams.append("keyphrase", keyphrase)

    if (publicBody) url.searchParams.append("publicBody", publicBody)
    if (dateStart) url.searchParams.append("dateStart", dateStart.toString())
    if (dateEnd) url.searchParams.append("dateEnd", dateEnd.toString())

    console.log(url.href)

    
    const json: Promise<any> = await requestJson(url)
    if (isSearchResponse(json)) {
      const resp: SearchResponse = json
      return resp;
    } else {
      console.log(json)
      throw new Error("not a search response")
    }
  }
  return getSearchResponse
}