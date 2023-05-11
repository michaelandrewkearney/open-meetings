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
    <div className={styles["SearchBar"]}>
      <input
        className={styles["search-input"]}
        aria-label="Search a Meeting or Public Body"
        value={searchInput}
        onChange={(e) => handleSearchValue(e.target.value)}
        placeholder="Search a Meeting or Public Body"
      />
    </div>
  );
}
