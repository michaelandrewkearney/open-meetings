import {
  Reducer,
  ReducerAction,
  ReducerState,
  useEffect,
  useReducer,
  useState,
} from "react";
import SearchBar from "../components/search/SearchBar";
import { RequestJsonFunction } from "../server/types";
import { SearchFilters, SearchResults } from "../meetingTypes";
import ResultsSection from "../components/search/ResultsSection";
import { buildSearch } from "../server/getSearch";
import { useLoaderData, useSearchParams } from "react-router-dom";
import { toDateObj, toDateStr } from "../components/search/date_utils";
import { FacetCount } from "../server/searchResponse";
import { SearchState, isSearchState } from "..";

interface SearchPageProps {
  requestJsonFunction: RequestJsonFunction;
}

function SearchPage({ requestJsonFunction }: SearchPageProps) {
  const loaderData: unknown = useLoaderData();
  if (!isSearchState(loaderData)) {
    throw new Error("Not a SearchState");
  }

  const initState: SearchState = loaderData;

  const [keyphrase, setKeyphrase] = useState<string>(initState.keyphrase);
  /** Map of body names to facet counts */
  const [bodyFacet, setBodyFacet] = useState<Map<string, number>>(
    initState.bodyFacet
  );

  const [filteredBodyFacet, setFilteredBodyFacet] = useState<
    Map<string, number>
  >(initState.filteredBodyFacet);
  const [filters, setFilters] = useState<SearchFilters>(initState.filters);
  const [results, setResults] = useState<SearchResults>(initState.results);

  const initSearchInput =
    initState.keyphrase === "*" ? "" : initState.keyphrase;
  const [searchInput, setSearchInput] = useState(initSearchInput);
  const [searchParams, setSearchParams] = useSearchParams();

  const getSearch = buildSearch(requestJsonFunction);

  useEffect(() => {
    setSearchParams(() => ({
      keyphrase: keyphrase,
      body: filters.body === null ? "all" : filters.body,
      ...(filters.dateStart && { dateStart: toDateStr(filters.dateStart) }),
      ...(filters.dateEnd && { dateEnd: toDateStr(filters.dateEnd) }),
    }));
  }, [filters, keyphrase]);

  const handleNewKeyphraseSearch = (
    newKeyphrase: string,
    newDateStart: Date | null,
    newDateEnd: Date | null
  ) => {
    const newFilters: SearchFilters = {
      body: null,
      dateStart: newDateStart,
      dateEnd: newDateEnd,
    };

    setKeyphrase(newKeyphrase);
    setFilters(() => newFilters);
    getSearch(newKeyphrase, newFilters).then((newResults: SearchResults) => {
      setResults(() => newResults);
      setBodyFacet(() => newResults.bodyFacetMap);
    });
  };

  const handleBodySelect = (body: string | null) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      body: body,
    }));

    getSearch(keyphrase, { ...filters, body: body }).then((newResults) =>
      setResults(() => newResults)
    );
  };

  const handleDate = (dateStart: Date | null, dateEnd: Date | null) => {
    setFilters((prevFilters) => ({
      body: prevFilters.body,
      dateStart: dateStart,
      dateEnd: dateEnd,
    }));

    if (dateStart === null && dateEnd === null) {
      setFilteredBodyFacet(() => bodyFacet);
      getSearch(keyphrase, {
        ...filters,
        dateStart: dateStart,
        dateEnd: dateEnd,
      }).then((newResults) => {
        setResults(() => newResults);
      });
      return;
    }

    getSearch(keyphrase, {
      ...filters,
      dateStart: dateStart,
      dateEnd: dateEnd,
    }).then((newResults) => {
      setResults(() => newResults);
      setFilteredBodyFacet(() => newResults.bodyFacetMap);
    });
  };

  return (
    <>
      <SearchBar
        keyphrase={searchInput}
        handleSearchValue={(value) => setSearchInput(value)}
        handleSearchSubmit={(e) => {
          e.preventDefault();
          handleNewKeyphraseSearch(
            searchInput === "" ? "*" : searchInput,
            filters.dateStart,
            filters.dateEnd
          );
        }}
      />
      {results && bodyFacet ? (
        <ResultsSection
          searchResults={results}
          handleBodySelect={handleBodySelect}
          handleDate={handleDate}
          searchParams={searchParams}
          filters={filters}
          bodyFacet={filteredBodyFacet}
          keyphrase={keyphrase}
        />
      ) : (
        <></>
      )}
    </>
  );
}

export default SearchPage;
