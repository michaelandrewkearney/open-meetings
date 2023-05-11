import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import "@testing-library/jest-dom";
import SearchBar from "../components/search/SearchBar";
import MeetingPage from "../routes/MeetingPage";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { Meeting } from "../meetingTypes";
import BodySelect from "../components/search/inputs/BodySelect";
test("search renders", async () => {
  let mockInputState = "";

  render(
    <SearchBar
      searchInput="*"
      handleSearchValue={(target) => {
        mockInputState = target;
      }}
    />
  );
  function delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
  (async () => {
    await delay(5000);
  })();
  expect(screen.getByRole("searchbox")).toBeInTheDocument();
  // verify page content for default route
  expect(
    screen.getByRole("search", { name: "Full-text Search" })
  ).toBeInTheDocument();

  expect(screen.getByRole("searchbox")).toBeInTheDocument();
});

test("meetingpage renders", async () => {
  const MOCK_MEETING: Meeting = {
    id: "1",
    body: "Rhode Island School Building Taskforce",
    meetingDate: new Date(2023, 4 - 1, 10),
    filingDate: new Date(2023, 4 - 1, 2),
    address:
      "East Providence High School - library, 2000 Pawtucket Avenue, East Providence, RI, 02914",
    isCancelled: false,
    is_annual_calendar: true,
    is_emergency: false,
    is_public_notice: false,
    latestAgenda: [
      "on the agenda is the following:",
      "discussing the taskforce",
      "the budget for the taskforce",
    ],
    latestAgendaLink:
      "https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4692%5C2023%5C457017.pdf",
    latestMinutes: [
      "today we are coming to gather a taskforce",
      "the taskforce has made progress along several front, the taskforce along several fronts including:",
      "improving bathroom facilities",
    ],
    latestMinutesLink:
      "https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath=%5CNotices%5C4495%5C2023%5C458152.pdf",
    contactPerson: "taskforce person",
    contactEmail: "taskforce@gmail.com",
    contactPhone: "(888)-888-8888",
  };

  const routes = [
    {
      path: "/meetings/:id",
      element: <MeetingPage />,
      loader: () => MOCK_MEETING,
    },
  ];

  const router = createMemoryRouter(routes, {
    initialEntries: ["/?keyphrase=*&body=all", "/meetings/1"],
  });

  render(<RouterProvider router={router} />);

  const headingName = `${
    MOCK_MEETING.body
  } on ${MOCK_MEETING.meetingDate.toLocaleDateString()}`;

  await waitFor(() => screen.getByRole("heading", { name: headingName }));
  expect(
    screen.getByRole("heading", { name: headingName })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "Back to Search" })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "View Latest Agenda PDF" })
  ).toBeInTheDocument();
  expect(
    screen.getByRole("link", { name: "View Latest Minutes PDF" })
  ).toBeInTheDocument();

  const infoRegion = screen.getByRole("region", {
    name: "Meeting Information",
  });
  expect(infoRegion).toHaveTextContent(MOCK_MEETING.address);
  expect(infoRegion).toHaveTextContent(MOCK_MEETING.contactEmail);
  expect(infoRegion).toHaveTextContent(MOCK_MEETING.contactPerson);
  expect(infoRegion).toHaveTextContent(MOCK_MEETING.contactPhone);
});

test("bodySelect renders", async () => {
  let mockBody: string | null = null;

  render(
    <BodySelect
      facetMap={
        new Map([
          ["mockBody1", 2],
          ["mockBody2", 1],
        ])
      }
      selectedBody={null}
      handleBodySelect={(body: string | null) => {
        mockBody = body;
      }}
    />
  );
  expect(
    screen.getByRole("radiogroup", { name: "Filter by Body" })
  ).toBeInTheDocument();
  const radioGroup = screen.getByRole("radiogroup", { name: "Filter by Body" });

  expect(
    within(radioGroup).getByRole("radio", { name: "All Bodies - 3 results" })
  ).toBeInTheDocument();
  expect(
    within(radioGroup).getByRole("radio", { name: "mockBody1 - 2 results" })
  ).toBeInTheDocument();
  const mockBody1Option = within(radioGroup).getByRole("radio", {
    name: "mockBody1 - 2 results",
  });
  expect(
    within(radioGroup).getByRole("radio", { name: "mockBody2 - 1 results" })
  ).toBeInTheDocument();
  expect(
    within(radioGroup).getByRole("radio", { name: "All Bodies - 3 results" })
  ).toBeChecked();
});
