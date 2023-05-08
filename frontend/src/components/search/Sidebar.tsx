import styles from "./Sidebar.module.css";

import { Search } from "../../meetingTypes";
import BodySelect from "./BodySelect";
import DateSelect from "./DateSelect";

interface SidebarProps {
  search: Search;
  handleBodySelect: any;
  handleDate: any;
  searchParams: URLSearchParams;
}

export default function Sidebar({
  search,
  handleBodySelect,
  handleDate,
  searchParams,
}: SidebarProps) {
  return (
    <aside className={styles["Sidebar"]}>
      <DateSelect handleDate={handleDate} searchParams={searchParams} />
      <BodySelect
        facetMap={search.bodyFacetMap}
        handleBodySelect={handleBodySelect}
        searchParams={searchParams}
      />
    </aside>
  );
}
