import { FormEvent, useState } from "react";
import "./App.css";
import SearchBar from "./components/SearchBar";
import { RequestJsonFunction } from "./server/types";
import { Search, SearchState } from "./meetingTypes";
import ResultSection from "./components/ResultSection";
import DateSelect from "./components/DateSelect";
import { buildSearch } from "./server/searchMeeting";

interface AppProps {
  requestJsonFunction: RequestJsonFunction;
}

function App({ requestJsonFunction }: AppProps) {
  const [keyphrase, setKeyphrase] = useState("");
  const [searchState, setSearchState] = useState<SearchState>({
    search: null,
    dateStart: null,
    dateEnd: null,
  });

  const runSearch = buildSearch(requestJsonFunction);

  const handleSearchSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    runSearch(keyphrase, null, searchState.dateStart, searchState.dateEnd).then(
      (newSearch: Search) =>
        setSearchState({
          search: newSearch,
          dateStart: searchState.dateStart,
          dateEnd: searchState.dateEnd,
        })
    );
  };

  const handleBodySelect = (body: string | null) => {
    if (searchState.search) {
      const oldSearch: Search = searchState.search;
      runSearch(
        oldSearch.keyphrase,
        body,
        searchState.dateStart,
        searchState.dateEnd
      ).then((newSearch: Search) => {
        setSearchState({
          search: {
            keyphrase: oldSearch.keyphrase,
            selectedBody: newSearch.selectedBody,
            bodyFacetMap: oldSearch.bodyFacetMap,
            resultsInfo: newSearch.resultsInfo,
            results: newSearch.results,
          },
          dateStart: searchState.dateStart,
          dateEnd: searchState.dateEnd,
        });
      });
    }
  };

  const handleDate = (dateStart: Date | null, dateEnd: Date | null) => {
    console.log(dateStart ? dateStart.toDateString() : null);

    if (searchState.search) {
      runSearch(
        searchState.search.keyphrase,
        searchState.search.selectedBody,
        dateStart,
        dateEnd
      ).then((newSearch: Search) =>
        setSearchState({
          search: newSearch,
          dateStart: dateStart,
          dateEnd: dateEnd,
        })
      );
    } else {
      setSearchState({
        search: null,
        dateStart: dateStart,
        dateEnd: dateEnd,
      });
    }
  };

  return (
    <div className="App">
      <SearchBar
        keyphrase={keyphrase}
        handleSearchValue={(value) => setKeyphrase(value)}
        handleSearchSubmit={handleSearchSubmit}
      />
      <DateSelect handleDate={handleDate} />
      {searchState.search ? (
        <ResultSection
          search={searchState.search}
          handleBodySelect={handleBodySelect}
        />
      ) : (
        <></>
      )}
    </div>
  );
}

export default App;
