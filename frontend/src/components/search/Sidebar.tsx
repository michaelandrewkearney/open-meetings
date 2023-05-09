import styles from "./Sidebar.module.css";

import { SearchResults } from "../../meetingTypes";
import DateSelect from "./inputs/DateSelect";
import BodySelect from "./inputs/BodySelect";

interface SidebarProps {
  searchResults: SearchResults;
  handleBodySelect: any;
  handleDate: any;
  searchParams: URLSearchParams;
}

export default function Sidebar({
  searchResults,
  handleBodySelect,
  handleDate,
  searchParams,
}: SidebarProps) {
  return (
    <form className={styles["Sidebar"]} aria-label="Search Filter Options">
      <DateSelect handleDate={handleDate} searchParams={searchParams} />
      <BodySelect
        facetMap={searchResults.bodyFacetMap}
        handleBodySelect={handleBodySelect}
        searchParams={searchParams}
      />
    </form>
  );
}
