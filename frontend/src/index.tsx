import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./routes/SearchPage";
import mockRequestJson from "./tests/mocks/mockRequestJson";
import { createBrowserRouter, Params, RouterProvider } from "react-router-dom";
import { RequestJsonFunction } from "./server/types";
import { buildGetMeeting } from "./server/getMeeting";
import MeetingInfo from "./routes/MeetingPage";
import fetchJson from "./server/fetchJson";

const REQUEST_JSON_FUNCTION: RequestJsonFunction = fetchJson;

const router = createBrowserRouter([
  {
    path: "/",
    element: <App requestJsonFunction={REQUEST_JSON_FUNCTION} />,
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
