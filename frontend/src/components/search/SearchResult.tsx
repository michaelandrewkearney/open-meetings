import styles from "./SearchResult.module.css";

import { MeetingResult, ResultHighlight } from "../../meetingTypes";
import { snippetToJSXElt } from "./parseMarks";
import { Link } from "react-router-dom";

interface SearchResultProps {
  result: MeetingResult;
}

export default function SearchResult({ result }: SearchResultProps) {
  const getBodyName = (): string => {
    const nameWithMarks: ResultHighlight | undefined = result.highlights.find(
      (highlight) => highlight.field === "body"
    );
    return nameWithMarks ? nameWithMarks.snippet : result.body;
  };

  const bodyName: JSX.Element = snippetToJSXElt(getBodyName());

  return (
    <div className={styles["SearchResult"]}>
      {result.isCancelled ? (
        <p className={styles["cancelled-text"]}>
          Cancelled {result.cancelledDate.toLocaleString()}
        </p>
      ) : (
        <></>
      )}
      <Link to={`meetings/${result.id}`}>
        <h3>{bodyName}</h3>
      </Link>
      <ul className={styles["result-metadata"]}>
        <p>{result.meetingDate.toLocaleString()}</p>
        <p>{result.address}</p>
      </ul>
      {result.highlights.map((highlight) =>
        ["latestAgenda", "latestMinutes"].includes(highlight.field) ? (
          <p className={styles["snippet"]} key={highlight.snippet}>
            {snippetToJSXElt(highlight.snippet)}
          </p>
        ) : (
          <></>
        )
      )}
      <hr />
    </div>
  );
}
