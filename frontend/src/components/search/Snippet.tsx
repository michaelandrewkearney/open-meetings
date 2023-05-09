import styles from "./Snippet.module.css";

import { MeetingResult } from "../../meetingTypes";
import { snippetToJSXElt } from "./parseMarks";

interface SnippetProps {
  result: MeetingResult;
}

export default function Snippet({ result }: SnippetProps) {
  let snippets: string[] = [];

  if (result.highlights && result.highlights.length > 0) {
    result.highlights.forEach((highlight) => {
      snippets =
        "snippets" in highlight
          ? highlight.snippets
          : (snippets = [highlight.snippet]);
    });
  } else if (result.latestAgendaPreview) {
    snippets = [result.latestAgendaPreview];
  }

  return (
    <>
      {snippets.map((snippet, index) => (
        <p className={styles["Snippet"]} key={index}>
          {snippetToJSXElt(snippet)}
        </p>
      ))}
    </>
  );
}
