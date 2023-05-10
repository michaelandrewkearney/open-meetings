import { FormEvent } from "react";
import styles from "./SearchBar.module.css";
import Logo from "../Logo";

interface SearchBarProps {
  searchInput: string;
  handleSearchValue: (target: string) => void;
}

export default function SearchBar({
  searchInput,
  handleSearchValue,
}: SearchBarProps) {
  return (
    <header className={styles["search-bar"]}>
      <Logo />
      <div className={styles["search-input-wrapper"]}>
        <input
          className={styles["search-input"]}
          aria-labelledby="search-label"
          value={searchInput}
          onChange={(e) => handleSearchValue(e.target.value)}
          placeholder="Search a Meeting or Public Body"
        />
      </div>
    </header>
  );
}
