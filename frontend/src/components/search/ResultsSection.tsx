import styles from "./ResultsSection.module.css";

import {
  MeetingResult,
  SearchFilters,
  SearchResults,
} from "../../meetingTypes";
import SearchResult from "./SearchResult";
import Sidebar from "./Sidebar";

interface ResultSectionProps {
  searchResults: SearchResults;
  handleBodySelect: (body: string | null) => void;
  handleDate: (dateStart: Date | null, dateEnd: Date | null) => void;
  searchParams: URLSearchParams;
  filters: SearchFilters;
  keyphrase: string;
}

export default function ResultSection({
  searchResults,
  handleBodySelect,
  handleDate,
  searchParams,
  filters,
  keyphrase,
}: ResultSectionProps) {
  const getDateFilterInfo = (): string => {
    if (!filters.dateStart && !filters.dateEnd) {
      return "anytime";
    }
    const dateStartInfo: string = filters.dateStart
      ? filters.dateStart.toLocaleDateString()
      : "anytime";
    const dateEndInfo: string = filters.dateEnd
      ? filters.dateEnd.toLocaleDateString()
      : "anytime";
    return `between ${dateStartInfo} and ${dateEndInfo}`;
  };

  const dateFilterInfo: string = getDateFilterInfo();

  return (
    <div className={styles.ResultsSection}>
      <Sidebar
        searchResults={searchResults}
        handleBodySelect={handleBodySelect}
        handleDate={handleDate}
        searchParams={searchParams}
      />
      <main id={styles["results"]} aria-label="Search results">
        <p aria-live="polite" role="presentation">
          {`${searchResults.resultsInfo.found} results `}
          <span className="sr-only">{` for ${keyphrase} from ${
            filters.body ? filters.body : "all bodies"
          }, ${dateFilterInfo}`}</span>
        </p>
        {searchResults.results.length != 0 ? (
          searchResults.results.map((result: MeetingResult) => (
            <SearchResult
              key={result.id}
              result={result}
              searchParams={searchParams}
            />
          ))
        ) : (
          <p>No results found</p>
        )}
      </main>
    </div>
  );
}
