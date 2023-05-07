import { FormEvent } from "react";
import styles from "./SearchBar.module.css";

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
    <header className={styles.SearchBar}>
      <a id={styles["logo"]}>
        <h1>
          <span id={styles["logo-small-text"]}>Rhode Island</span>
          <span id={styles["logo-big-text"]}>Open Meetings</span>
        </h1>
      </a>
      <form
        id={styles["search-form"]}
        aria-label="meeting search"
        onSubmit={(e) => handleSearchSubmit(e)}
      >
        <label id={styles["search-label"]} htmlFor="search-input">
          Meeting or Public Body
        </label>
        <input
          type="search"
          id={styles["search-input"]}
          aria-labelledby="search-label"
          value={keyphrase}
          onChange={(e) => handleSearchValue(e.target.value)}
        />
        <button>Search</button>
      </form>
    </header>
  );
}
