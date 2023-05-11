import styles from "./MeetingPage.module.css";
import { Link, useLoaderData, useLocation } from "react-router-dom";
import { Meeting, isMeeting } from "../meetingTypes";
import Logo from "../components/Logo";

export default function MeetingPage() {
  const loaderData: unknown = useLoaderData();
  if (!isMeeting(loaderData)) {
    throw new Error("Could not retrieve meeting");
  }
  const meeting: Meeting = loaderData;

  const { state } = useLocation();
  const prevPath = state ? `/?${state.prevQuery}` : "/";

  const meetingInfo: Array<{ label: string; info: string }> = [
    { label: "Address", info: meeting.address },
    { label: "Time", info: meeting.meetingDate.toLocaleString() },
    { label: "Filed on", info: meeting.filingDate.toLocaleString() },
  ];

  const attrs = [];
  if (meeting.is_emergency) attrs.push("Emergency Meeting");
  if (meeting.is_annual_calendar) attrs.push("Annual Calendar");
  if (meeting.is_public_notice) attrs.push("Public Announcement");

  document.title = "Open Meetings";

  return (
    <>
      <header className={styles["header"]}>
        <Logo />
      </header>
      <div className="page-body">
        <nav id={styles["back-nav"]}>
          <Link to={prevPath}>Back to Search</Link>
        </nav>
        <main id={styles["page-content"]}>
          {meeting.isCancelled ? (
            <div id={styles["cancelled-detail"]}>
              <p id={styles["cancelled-time"]}>
                Cancelled on {meeting.cancelledDate.toLocaleString()}
              </p>
              <p>Reason: {meeting.cancelledReason}</p>
            </div>
          ) : (
            <></>
          )}
          <h1>
            {meeting.body} on {meeting.meetingDate.toLocaleDateString()}
          </h1>
          <div id={styles["meeting-attrs"]}>
            <span key={attrs.join(",")}>{attrs.join(", ")}</span>
          </div>
          <section aria-label="Meeting Information" id={styles["meeting-info"]}>
            <div>
              {meetingInfo.map(({ label, info }) => (
                <p
                  key={label}
                  className={styles["meeting-detail"]}
                  role="presentation"
                >
                  <span
                    className={styles["label"]}
                    id={label}
                  >{`${label}:`}</span>
                  <span className={styles["info"]}>{info}</span>
                </p>
              ))}
            </div>

            <p className={styles["meeting-detail"]} id={styles["contact-info"]}>
              <span className={styles["label"]}>Contact:</span>
              <span className={styles["info"]}>
                <span>{meeting.contactPerson}</span>
                <span>{meeting.contactEmail}</span>
                <span>{meeting.contactPhone}</span>
              </span>
            </p>
          </section>
          <hr />
          <section aria-label="Minutes and Agenda">
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
          </section>
        </main>
      </div>
    </>
  );
}

interface DocumentSectionProps {
  title: string;
  link: string | null;
  paragraphs: string[] | null;
}

const DocumentSection = ({ title, link, paragraphs }: DocumentSectionProps) => (
  <div className={styles.DocumentSection}>
    <div className={styles["doc-section-title"]}>
      <h2 id={title}>{title}</h2>
      {link ? (
        <a href={link ? link : undefined} aria-label={`View ${title} PDF`}>
          View PDF
        </a>
      ) : (
        <></>
      )}
    </div>
    {paragraphs ? (
      paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)
    ) : (
      <i>No data available</i>
    )}
  </div>
);
