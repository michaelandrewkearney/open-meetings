import styles from "./SearchResult.module.css";

import { MeetingResult, ResultHighlight } from "../../meetingTypes";
import { snippetToJSXElt } from "./parseMarks";
import { Link } from "react-router-dom";
import Snippet from "./Snippet";

interface SearchResultProps {
  result: MeetingResult;
  searchParams: URLSearchParams;
}

export default function SearchResult({
  result,
  searchParams,
}: SearchResultProps) {
  const getBodyName = (): string => {
    const nameWithMarks: ResultHighlight | undefined = result.highlights?.find(
      (highlight) => highlight.field === "body"
    );
    if (nameWithMarks && "snippet" in nameWithMarks) {
      return nameWithMarks.snippet;
    }
    return result.body;
  };

  const bodyName: JSX.Element = snippetToJSXElt(getBodyName());

  return (
    <div className={styles["SearchResult"]}>
      <Link
        to={`meetings/${result.id}`}
        state={{ prevQuery: searchParams.toString() }}
      >
        <h3>
          {bodyName} on {result.meetingDate.toLocaleDateString()}
        </h3>
      </Link>
      {result.isCancelled ? (
        <p className={styles["cancelled-text"]}>
          Cancelled {result.cancelledDate.toLocaleString()}
        </p>
      ) : (
        <></>
      )}
      <Snippet result={result} />
      <hr aria-hidden="true" />
    </div>
  );
}
