import { Link, useLoaderData } from "react-router-dom";
import { Meeting, isMeeting } from "../meetingTypes";

export default function MeetingInfo() {
  const loaderData: unknown = useLoaderData();
  if (!isMeeting(loaderData)) {
    throw new Error("Could not retrieve meeting");
  }
  const meeting: Meeting = loaderData;

  return (
    <>
      <Link to="/">Back to Search</Link>
      <h1>
        {meeting.body} on {meeting.meetingDate.toLocaleDateString()}
      </h1>
      <p>address: {meeting.address}</p>

      <DocumentSection
        title="Latest Agenda"
        link={meeting.latestAgendaLink}
        paragraphs={meeting.latestAgenda}
      />

      <DocumentSection
        title="Latest Minutes"
        link={meeting.latestMinutesLink}
        paragraphs={meeting.latestMinutes}
      />
    </>
  );
}

interface DocumentSectionProps {
  title: string;
  link: string | null;
  paragraphs: string[] | null;
}

const DocumentSection = ({ title, link, paragraphs }: DocumentSectionProps) => (
  <>
    <h2>{title}</h2>
    <a href={link ? link : undefined}>View PDF</a>
    {paragraphs ? (
      paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)
    ) : (
      <></>
    )}
  </>
);
