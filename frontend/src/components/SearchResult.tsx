import styles from "./SearchResult.module.css";

import { MeetingResult } from "../meetingTypes";

interface SearchResultProps {
  result: MeetingResult;
}

export default function SearchResult({ result }: SearchResultProps) {
  return (
    <div className={styles["SearchResult"]}>
      {result.isCancelled ? (
        <p className={styles["cancelled-text"]}>
          Cancelled {result.cancelledDate.toLocaleString()}
        </p>
      ) : (
        <></>
      )}
      <h3>{result.body}</h3>
      <ul className={styles["result-metadata"]}>
        <p>{result.meetingDate.toLocaleString()}</p>
        <p>{result.address}</p>
      </ul>
      <p className={styles["snippet"]}>
        placeholder snippet text to replace with dynamic snippets
      </p>
      <hr />
    </div>
  );
}
