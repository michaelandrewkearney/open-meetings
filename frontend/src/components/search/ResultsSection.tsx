import styles from "./ResultsSection.module.css";

import { MeetingResult, SearchResults } from "../../meetingTypes";
import SearchResult from "./SearchResult";
import Sidebar from "./Sidebar";

interface ResultSectionProps {
  searchResults: SearchResults;
  handleBodySelect: (body: string | null) => void;
  handleDate: (dateStart: Date | null, dateEnd: Date | null) => void;
  searchParams: URLSearchParams;
}

export default function ResultSection({
  searchResults,
  handleBodySelect,
  handleDate,
  searchParams,
}: ResultSectionProps) {
  return (
    <div className={styles.ResultsSection}>
      <Sidebar
        searchResults={searchResults}
        handleBodySelect={handleBodySelect}
        handleDate={handleDate}
        searchParams={searchParams}
      />
      <main id={styles["results"]}>
        {searchResults.results.map((result: MeetingResult) => (
          <SearchResult
            key={result.id}
            result={result}
            searchParams={searchParams}
          />
        ))}
      </main>
    </div>
  );
}
