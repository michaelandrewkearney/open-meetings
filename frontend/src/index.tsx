import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import {
  createBrowserRouter,
  LoaderFunctionArgs,
  Params,
  RouterProvider,
  Route
} from "react-router-dom";
import { RequestJsonFunction } from "./server/types";
import { buildGetMeeting } from "./server/getMeeting";
import MeetingInfo from "./routes/MeetingPage";
import fetchJson from "./server/fetchJson";
import { SearchFilters, SearchResults } from "./meetingTypes";
import { buildSearch } from "./server/getSearch";
import { toDateObj } from "./components/search/date_utils";
import SearchPage, { buildInitialSearch } from "./routes/SearchPage";

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

const router = createBrowserRouter([
  {
    path: "/",
    element: <SearchPage requestJsonFunction={REQUEST_JSON_FUNCTION} />,
    loader: buildInitialSearch(REQUEST_JSON_FUNCTION),
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
