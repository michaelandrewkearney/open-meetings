import styles from "./Sidebar.module.css";

import { SearchFilters } from "../../meetingTypes";
import DateSelect from "./inputs/DateSelect";
import BodySelect from "./inputs/BodySelect";

interface SidebarProps {
  handleBodySelect: any;
  handleDate: any;
  searchParams: URLSearchParams;
  filters: SearchFilters;
  bodyFacet: Map<string, number>;
}

export default function Sidebar({
  handleBodySelect,
  handleDate,
  searchParams,
  bodyFacet,
  filters,
}: SidebarProps) {
  return (
    <form className={styles["Sidebar"]} aria-label="Filter Options">
      <DateSelect handleDate={handleDate} searchParams={searchParams} />
      <BodySelect
        facetMap={bodyFacet}
        selectedBody={filters.body}
        handleBodySelect={handleBodySelect}
      />
    </form>
  );
}
