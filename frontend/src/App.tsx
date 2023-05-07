import styles from "./App.module.css";

import { FormEvent, useEffect, useState } from "react";
import SearchBar from "./components/search/SearchBar";
import { RequestJsonFunction } from "./server/types";
import { Search, SearchState } from "./meetingTypes";
import ResultsSection from "./components/search/ResultsSection";
import { buildSearch } from "./server/getSearch";
import { useSearchParams } from "react-router-dom";

interface AppProps {
  requestJsonFunction: RequestJsonFunction;
}

function App({ requestJsonFunction }: AppProps) {
  const [keyphrase, setKeyphrase] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchState, setSearchState] = useState<SearchState>({
    search: null,
    dateStart: null,
    dateEnd: null,
  });

  const getSearch = buildSearch(requestJsonFunction);

  const runSearch = (keyphrase: string) => {
    getSearch(keyphrase, null, searchState.dateStart, searchState.dateEnd).then(
      (newSearch: Search) =>
        setSearchState({
          search: newSearch,
          dateStart: searchState.dateStart,
          dateEnd: searchState.dateEnd,
        })
    );
  };

  useEffect(() => {
    if (!searchParams.has("query")) {
      return;
    }
    const query: string = searchParams.get("query")!;
    if (query === "*") {
      runSearch("");
      setKeyphrase("");
    } else {
      runSearch(query);
      setKeyphrase(query);
    }
  }, []);

  const handleSearchSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const query: string = keyphrase === "" ? "*" : keyphrase;
    const body: string | undefined | null = searchState.search?.selectedBody;
    setSearchParams({
      query: query,
      ...(body != undefined && { body: body === null ? "all" : body }),
    });
    runSearch(keyphrase);
  };

  const handleBodySelect = (body: string | null) => {
    console.log(body);
    setSearchParams({
      query: searchParams.get("query")!,
      body: body === null ? "all" : body,
    });
    if (searchState.search) {
      const oldSearch: Search = searchState.search;
      getSearch(
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
    setSearchParams({
      query: searchParams.get("query")!,
      body: searchParams.get("body")!,
      ...(dateStart && { dateStart: dateStart.getTime().toString() }),
      ...(dateEnd && { dateEnd: dateEnd.getTime().toString() }),
    });

    if (searchState.search) {
      getSearch(
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
      {searchState.search ? (
        <ResultsSection
          search={searchState.search}
          handleBodySelect={handleBodySelect}
          handleDate={handleDate}
          searchParams={searchParams}
        />
      ) : (
        <></>
      )}
    </div>
  );
}

export default App;
