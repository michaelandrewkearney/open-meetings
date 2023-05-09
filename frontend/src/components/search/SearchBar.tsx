import { FormEvent } from "react";
import styles from "./SearchBar.module.css";
import Logo from "../Logo";

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
    <div className={styles.SearchBar}>
      <Logo />
      <form
        id={styles["search-form"]}
        aria-label="Full-text Search"
        onSubmit={(e) => handleSearchSubmit(e)}
        role="search"
      >
        <label id={styles["search-label"]} htmlFor="search-input">
          Search a Meeting or Public Body
        </label>
        <input
          type="search"
          id={styles["search-input"]}
          aria-labelledby="search-label"
          value={keyphrase}
          onChange={(e) => handleSearchValue(e.target.value)}
        />
        <input type="submit" value="Search" aria-label="Search meetings" />
      </form>
    </div>
  );
}
