import { useEffect, useState } from "react";
import SearchBar from "../components/search/SearchBar";
import { RequestJsonFunction } from "../server/types";
import { SearchFilters, SearchResults } from "../meetingTypes";
import ResultsSection from "../components/search/ResultsSection";
import { buildSearch } from "../server/getSearch";
import {
  LoaderFunctionArgs,
  useLoaderData,
  useSearchParams,
} from "react-router-dom";
import { toDateObj, toDateStr } from "../components/search/date_utils";
import { SearchState, isSearchState } from "..";
import styles from "./SearchPage.module.css";

export function buildInitialSearch(requestJsonFunc: RequestJsonFunction) {
  async function initialSearch({
    request,
  }: LoaderFunctionArgs): Promise<SearchState> {
    const search = buildSearch(requestJsonFunc);
    const url = new URL(request.url);
    const params = {
      keyphrase: url.searchParams.get("keyphrase"),
      body: url.searchParams.get("body"),
      dateStart: url.searchParams.get("dateStart"),
      dateEnd: url.searchParams.get("dateEnd"),
    };

    const defaultFilters = { body: null, dateStart: null, dateEnd: null };

    if (!params.keyphrase) {
      const allMeetings: SearchResults = await search("*", defaultFilters);
      return {
        keyphrase: "*",
        filters: defaultFilters,
        bodyFacet: allMeetings.bodyFacetMap,
        filteredBodyFacet: allMeetings.bodyFacetMap,
        results: allMeetings,
      };
    } else {
      const filters: SearchFilters = {
        body: params.body === "all" ? null : params.body,
        dateStart: params.dateStart ? toDateObj(params.dateStart) : null,
        dateEnd: params.dateEnd ? toDateObj(params.dateEnd) : null,
      };
      const keywordOnly = await search(params.keyphrase, defaultFilters);
      const bodyFacet = keywordOnly.bodyFacetMap;
      const filteredResults = await search(params.keyphrase, filters);

      let filteredBodyFacet: Map<string, number>;
      if (filters.dateStart === null && filters.dateEnd === null) {
        filteredBodyFacet = bodyFacet;
      } else {
        filteredBodyFacet = filteredResults.bodyFacetMap;
      }

      return {
        keyphrase: params.keyphrase,
        filters: filters,
        bodyFacet: bodyFacet,
        filteredBodyFacet: filteredBodyFacet,
        results: filteredResults,
      };
    }
  }
  return initialSearch;
}

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

  useEffect(() => {
    let prevSearchInput: string = searchInput;
    const timeoutId = setTimeout(() => {
      if (prevSearchInput == searchInput) {
        setKeyphrase(searchInput === "" ? "*" : searchInput);
      }
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [searchInput]);

  const handleNewKeyphraseSearch = () => {
    const newFilters: SearchFilters = {
      body: null,
      dateStart: null,
      dateEnd: null,
    };
    setFilters(() => newFilters);
    getSearch(keyphrase, newFilters).then((newResults: SearchResults) => {
      setResults(() => newResults);
      setBodyFacet(() => newResults.bodyFacetMap);
      setFilteredBodyFacet(() => newResults.bodyFacetMap);
    });
  };

  useEffect(() => {
    handleNewKeyphraseSearch();
  }, [keyphrase]);

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
      ...prevFilters,
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
    }

    getSearch(keyphrase, {
      body: null,
      dateStart: dateStart,
      dateEnd: dateEnd,
    }).then((newResults) => {
      setResults(() => newResults);
      if (dateStart === null && dateEnd === null) {
        setFilteredBodyFacet(() => bodyFacet);
      } else {
        // update only the facet counts
        console.log(newResults.bodyFacetMap);
        const filteredFacet: Map<string, number> = new Map();
        for (const body of bodyFacet.keys()) {
          console.log(body);
          const newFacetCount: number | undefined =
            newResults.bodyFacetMap.get(body);
          filteredFacet.set(body, newFacetCount ? newFacetCount : 0);
        }
        setFilteredBodyFacet(() => filteredFacet);
      }
    });
  };

  document.title = "Open Meetings";

  return (
    <>
      <SearchBar
        searchInput={searchInput}
        handleSearchValue={(value) => setSearchInput(value)}
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
