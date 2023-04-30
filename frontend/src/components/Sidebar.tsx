import styles from "./Sidebar.module.css";

import { Search } from "../meetingTypes";
import BodySelect from "./BodySelect";
import DateSelect from "./DateSelect";

interface SidebarProps {
  search: Search;
  handleBodySelect: any;
  handleDate: any;
}

export default function Sidebar({
  search,
  handleBodySelect,
  handleDate,
}: SidebarProps) {
  return (
    <aside className={styles["Sidebar"]}>
      <DateSelect handleDate={handleDate} />
      <BodySelect
        facetMap={search.bodyFacetMap}
        handleBodySelect={handleBodySelect}
      />
    </aside>
  );
}
