import styles from "./Snippet.module.css";

import { ResultHighlight } from "../../meetingTypes";
import { snippetToJSXElt } from "./parseMarks";

interface SnippetProps {
  highlight: ResultHighlight;
}

export default function Snippet({ highlight }: SnippetProps) {
  return (
    <>
      {"snippet" in highlight ? (
        <p className={styles["snippet"]} key={JSON.stringify(highlight)}>
          {snippetToJSXElt(highlight.snippet)}
        </p>
      ) : (
        <p className={styles["snippet"]} key={JSON.stringify(highlight)}>
          {snippetToJSXElt(highlight.snippets[0])}
        </p>
      )}
    </>
  );
}
