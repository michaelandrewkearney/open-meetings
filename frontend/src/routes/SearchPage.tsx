import { useEffect, useState } from "react";
import SearchBar from "../components/search/SearchBar";
import { RequestJsonFunction } from "../server/types";
import { SearchFilters, SearchResults } from "../meetingTypes";
import ResultsSection from "../components/search/ResultsSection";
import { buildSearch } from "../server/getSearch";
import { useSearchParams } from "react-router-dom";
import { toDateObj, toDateStr } from "../components/search/date_utils";

interface SearchPageProps {
  requestJsonFunction: RequestJsonFunction;
}

function SearchPage({ requestJsonFunction }: SearchPageProps) {
  const getSearch = buildSearch(requestJsonFunction);

  const [searchInput, setSearchInput] = useState("");
  const [searchParams, setSearchParams] = useSearchParams();
  const [keyphrase, setKeyphrase] = useState<string>();
  const [filters, setFilters] = useState<SearchFilters>({
    body: null,
    dateStart: null,
    dateEnd: null,
  });
  const [results, setResults] = useState<SearchResults>();

  useEffect(() => {
    console.log([...searchParams.entries()]);
    const keyphraseParam = searchParams.get("keyphrase");
    if (keyphraseParam === null) {
      console.log("making new search");
      setKeyphrase("*");
      handleNewSearch("*", { body: null, dateStart: null, dateEnd: null });
    } else {
      const bodyParam = searchParams.get("body");
      const dateStartParam = searchParams.get("dateStart");
      const dateEndParam = searchParams.get("dateEnd");

      handleNewSearch(keyphraseParam, {
        body: bodyParam === "all" ? null : bodyParam,
        dateStart: dateStartParam ? toDateObj(dateStartParam) : null,
        dateEnd: dateEndParam ? toDateObj(dateEndParam) : null,
      });
    }
  }, []);

  // useEffect(() => {
  //   if (keyphrase) {
  //     setSearchParams({
  //       keyphrase: keyphrase,
  //       body: filters.body ? filters.body : "all",
  //       ...(filters.dateStart && {
  //         dateStart: toDateStr(filters.dateStart),
  //       }),
  //       ...(filters.dateEnd && { dateEnd: toDateStr(filters.dateEnd) }),
  //     });
  //   }
  // }, [keyphrase]);

  const handleNewSearch = (newKeyphrase: string, newFilters: SearchFilters) => {
    setKeyphrase(newKeyphrase);

    getSearch(newKeyphrase, {
      body: null,
      dateEnd: null,
      dateStart: null,
    }).then((newResults: SearchResults) => {
      handleFilters(newKeyphrase, newFilters, newResults);
    });
  };

  const handleFilters = (
    keyphrase: string | undefined,
    newFilters: SearchFilters,
    resultsToFilter: SearchResults | undefined
  ) => {
    if (!keyphrase || !resultsToFilter) return;
    setFilters(newFilters);

    setSearchParams(() => ({
      keyphrase: keyphrase,
      body: newFilters.body ? newFilters.body : "all",
      ...(newFilters.dateStart && {
        dateStart: toDateStr(newFilters.dateStart),
      }),
      ...(newFilters.dateEnd && { dateEnd: toDateStr(newFilters.dateEnd) }),
    }));

    getSearch(keyphrase, newFilters).then((newResults: SearchResults) =>
      setResults({ ...newResults, bodyFacetMap: resultsToFilter.bodyFacetMap })
    );
  };

  const handleBodySelect = (body: string | null) => {
    handleFilters(keyphrase, { ...filters, body: body }, results);
  };

  const handleDate = (dateStart: Date | null, dateEnd: Date | null) => {
    handleFilters(
      keyphrase,
      { ...filters, dateStart: dateStart, dateEnd: dateEnd },
      results
    );
  };

  return (
    <div className="App">
      <SearchBar
        keyphrase={searchInput}
        handleSearchValue={(value) => setSearchInput(value)}
        handleSearchSubmit={(e) => {
          e.preventDefault();
          handleNewSearch(searchInput === "" ? "*" : searchInput, filters);
        }}
      />
      {results ? (
        <ResultsSection
          searchResults={results}
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

export default SearchPage;
