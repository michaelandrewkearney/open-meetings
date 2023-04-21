import { FormEvent } from "react";

interface SearchBarProps {
  keyphrase: string;
  handleSearchValue: (target: string) => void;
  handleSearchSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

export default function SearchBar({
  keyphrase,
  handleSearchValue,
  handleSearchSubmit,
}: SearchBarProps) {
  return (
    <>
      <form aria-label="meeting search" onSubmit={(e) => handleSearchSubmit(e)}>
        <label id="search-label" htmlFor="search">
          Search for a meeting
        </label>
        <input
          type="search"
          id="search"
          aria-labelledby="search-label"
          value={keyphrase}
          onChange={(e) => handleSearchValue(e.target.value)}
        />
        <button>Search</button>
      </form>
    </>
  );
}
