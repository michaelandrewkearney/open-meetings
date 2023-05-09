import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./routes/SearchPage";
import {
  createBrowserRouter,
  LoaderFunctionArgs,
  Params,
  RouterProvider,
} from "react-router-dom";
import { RequestJsonFunction } from "./server/types";
import { buildGetMeeting } from "./server/getMeeting";
import MeetingInfo from "./routes/MeetingPage";
import fetchJson from "./server/fetchJson";
import { SearchFilters, SearchResults } from "./meetingTypes";
import { buildSearch } from "./server/getSearch";
import { toDateObj } from "./components/search/date_utils";

const REQUEST_JSON_FUNCTION: RequestJsonFunction = fetchJson;

export interface SearchState {
  keyphrase: string;
  filters: SearchFilters;
  bodyFacet: Map<string, number>;
  filteredBodyFacet: Map<string, number>;
  results: SearchResults;
}

export function isSearchState(target: any): target is SearchState {
  const requiredParams = [
    "keyphrase",
    "filters",
    "bodyFacet",
    "results",
    "filteredBodyFacet",
  ];
  requiredParams.forEach((param) => {
    if (!(param in target)) {
      return false;
    }
  });
  return true;
}

async function initialSearch({
  request,
}: LoaderFunctionArgs): Promise<SearchState> {
  const search = buildSearch(REQUEST_JSON_FUNCTION);
  const url = new URL(request.url);
  const params = {
    keyphrase: url.searchParams.get("keyphrase"),
    body: url.searchParams.get("body"),
    dateStart: url.searchParams.get("dateStart"),
    dateEnd: url.searchParams.get("dateEnd"),
  };

  const defaultFilters = { body: null, dateStart: null, dateEnd: null };

  if (!params.keyphrase) {
    const allMeetings: SearchResults = await search("*", defaultFilters);
    return {
      keyphrase: "*",
      filters: defaultFilters,
      bodyFacet: allMeetings.bodyFacetMap,
      filteredBodyFacet: allMeetings.bodyFacetMap,
      results: allMeetings,
    };
  } else {
    const filters: SearchFilters = {
      body: params.body === "all" ? null : params.body,
      dateStart: params.dateStart ? toDateObj(params.dateStart) : null,
      dateEnd: params.dateEnd ? toDateObj(params.dateEnd) : null,
    };
    const keywordOnly = await search(params.keyphrase, defaultFilters);
    const bodyFacet = keywordOnly.bodyFacetMap;
    const filteredResults = await search(params.keyphrase, filters);

    let filteredBodyFacet: Map<string, number>;
    if (filters.dateStart === null && filters.dateEnd === null) {
      filteredBodyFacet = bodyFacet;
    } else {
      filteredBodyFacet = filteredResults.bodyFacetMap;
    }

    return {
      keyphrase: params.keyphrase,
      filters: filters,
      bodyFacet: bodyFacet,
      filteredBodyFacet: filteredBodyFacet,
      results: filteredResults,
    };
  }
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <App requestJsonFunction={REQUEST_JSON_FUNCTION} />,
    loader: initialSearch,
  },
  {
    path: "meetings/:meetingID",
    element: <MeetingInfo />,
    loader: async ({ params }: { params: Params<string> }) => {
      const getMeeting = buildGetMeeting(REQUEST_JSON_FUNCTION);
      return getMeeting(params.meetingID);
    },
  },
]);

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
