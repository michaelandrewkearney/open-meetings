import styles from "./Sidebar.module.css";

import { SearchFilters } from "../../meetingTypes";
import DateSelect from "./inputs/DateSelect";
import BodySelect from "./inputs/BodySelect";

interface SidebarProps {
  handleBodySelect: any;
  handleDate: any;
  filters: SearchFilters;
  bodyFacet: Map<string, number>;
}

export default function Sidebar({
  handleBodySelect,
  handleDate,
  bodyFacet,
  filters,
}: SidebarProps) {
  return (
    <section className={styles["Sidebar"]} aria-label="Filter Options">
      <DateSelect handleDate={handleDate} />
      <BodySelect
        facetMap={bodyFacet}
        selectedBody={filters.body}
        handleBodySelect={handleBodySelect}
      />
    </section>
  );
}
