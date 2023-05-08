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
  const [keyphrase, setKeyphrase] = useState<string>("*");
  const [filters, setFilters] = useState<SearchFilters>({
    body: null,
    dateStart: null,
    dateEnd: null,
  });
  const [results, setResults] = useState<SearchResults>();

  // useEffect(() => {
  //   console.log([...searchParams.entries()]);
  //   const keyphraseParam = searchParams.get("keyphrase");
  //   if (keyphraseParam === null) {
  //     console.log("making new search");
  //     setKeyphrase("*");
  //     handleNewKeyphraseSearch("*", {
  //       body: null,
  //       dateStart: null,
  //       dateEnd: null,
  //     });
  //   } else {
  //     const bodyParam = searchParams.get("body");
  //     const dateStartParam = searchParams.get("dateStart");
  //     const dateEndParam = searchParams.get("dateEnd");

  //     handleNewKeyphraseSearch(keyphraseParam, {
  //       body: bodyParam === "all" ? null : bodyParam,
  //       dateStart: dateStartParam ? toDateObj(dateStartParam) : null,
  //       dateEnd: dateEndParam ? toDateObj(dateEndParam) : null,
  //     });
  //   }
  // }, []);

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

  useEffect(() => {
    const params = {
      keyphrase: searchParams.get("keyphrase"),
      body: searchParams.get("body"), // === "all" ? null : searchParams.get("body")
      dateStart: searchParams.get("dateStart"),
      dateEnd: searchParams.get("dateEnd"),
    };

    if (!params.keyphrase) return;

    const newFilters: SearchFilters = {
      body: params.body === "all" ? null : params.body,
      dateStart: params.dateStart ? toDateObj(params.dateStart) : null,
      dateEnd: params.dateEnd ? toDateObj(params.dateEnd) : null,
    };

    searchFromParams(params.keyphrase, newFilters);
  }, []);

  // useEffect(() => {
  //   const params = {
  //     keyphrase: searchParams.get("keyphrase"),
  //     body: searchParams.get("body"), // === "all" ? null : searchParams.get("body")
  //     dateStart: searchParams.get("dateStart"),
  //     dateEnd: searchParams.get("dateStart"),
  //   };

  //   if (!params.keyphrase) {
  //     searchFromParams("*", { body: null, dateStart: null, dateEnd: null });

  //     setSearchParams(() => ({
  //       keyphrase: "*",
  //       body: "all",
  //     }));
  //     return;
  //   }

  //   const newFilters: SearchFilters = {
  //     body: params.body === "all" ? null : params.body,
  //     dateStart: params.dateStart ? toDateObj(params.dateStart) : null,
  //     dateEnd: params.dateEnd ? toDateObj(params.dateEnd) : null,
  //   };
  //   searchFromParams(params.keyphrase, newFilters);
  // }, []);

  async function searchFromParams(
    newKeyphrase: string,
    newFilters: SearchFilters
  ) {
    const newInput: string = newKeyphrase === "*" ? "" : newKeyphrase;
    setSearchInput(() => newInput);
    setKeyphrase(() => newKeyphrase);
    setFilters(() => ({ ...newFilters }));

    // get results without filtering by body so we can get facet map
    const initialResults = await getSearch(newKeyphrase, {
      ...newFilters,
      body: null,
    });

    const bodyFacetMap = initialResults.bodyFacetMap;

    const filteredByBody: SearchResults = await getSearch(
      newKeyphrase,
      newFilters
    );

    setResults(() => ({ ...filteredByBody, bodyFacetMap: bodyFacetMap }));

    // // set results to filtered by body results, with the old bodyFacetMap
    // const filteredByBody: SearchResults = await getSearch(
    //   newKeyphrase,
    //   newFilters
    // );
    // const newInput: string = newKeyphrase === "*" ? "" : newKeyphrase;
    // setSearchInput(() => newInput);
    // setKeyphrase(() => newKeyphrase);
    // setFilters(() => newFilters);
    // setResults(() => ({
    //   ...filteredByBody,
    //   bodyFacetMap: bodyFacetMap,
    // }));
  }

  const handleNewKeyphraseSearch = (
    newKeyphrase: string,
    newDateStart: Date | null,
    newDateEnd: Date | null
  ) => {
    setKeyphrase(newKeyphrase);
    const newFilters: SearchFilters = {
      body: null,
      dateStart: newDateStart,
      dateEnd: newDateEnd,
    };

    setFilters(() => newFilters);
    getSearch(newKeyphrase, newFilters).then((newResults: SearchResults) => {
      setResults(() => newResults);
    });
  };

  const handleBodySelect = (body: string | null) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      body: body,
    }));

    getSearch(keyphrase, { ...filters, body: body }).then((newResults) =>
      setResults((prevResults) => {
        console.log({ ...filters, body: body });
        console.log(newResults);
        if (prevResults) {
          console.log({
            ...newResults,
            bodyFacetMap: prevResults.bodyFacetMap,
          });
          return { ...newResults, bodyFacetMap: prevResults.bodyFacetMap };
        } else {
          return newResults;
        }
      })
    );
  };

  useEffect(() => {
    setSearchParams(() => ({
      keyphrase: keyphrase,
      body: filters.body === null ? "all" : filters.body,
      ...(filters.dateStart && { dateStart: toDateStr(filters.dateStart) }),
      ...(filters.dateEnd && { dateEnd: toDateStr(filters.dateEnd) }),
    }));
  }, [filters, keyphrase]);

  const handleDate = (dateStart: Date | null, dateEnd: Date | null) => {
    setFilters((prevFilters) => ({
      body: prevFilters.body,
      dateStart: dateStart,
      dateEnd: dateEnd,
    }));

    getSearch(keyphrase, {
      ...filters,
      dateStart: dateStart,
      dateEnd: dateEnd,
    }).then((newResults) => setResults(() => newResults));
  };

  return (
    <div className="App">
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
