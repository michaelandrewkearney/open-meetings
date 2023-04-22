import { FormEvent } from "react";
import { MeetingResult, Search, SearchState } from "../meetingTypes";
import BodySelect from "./BodySelect";
import SearchResult from "./SearchResult";

interface ResultSectionProps {
  search: Search;
  handleBodySelect: (body: string | null) => void;
}

export default function ResultSection({
  search,
  handleBodySelect,
}: ResultSectionProps) {
  return (
    <>
      <BodySelect
        facetMap={search.bodyFacetMap}
        handleBodySelect={handleBodySelect}
      />
      {search.results.map((result: MeetingResult) => (
        <SearchResult key={result.id} result={result} />
      ))}
    </>
  );
}
