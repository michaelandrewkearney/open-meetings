import { useLoaderData } from "react-router-dom";
import { toDateObj, toDateStr } from "../date_utils";
import styles from "./DateSelect.module.css";
import { useEffect, useRef, useState } from "react";
import { isSearchState } from "../../..";

interface DateSelectProps {
  handleDate: (startDate: Date | null, endDate: Date | null) => void;
  searchParams: URLSearchParams;
}

export default function DateSelect({
  handleDate,
  searchParams,
}: DateSelectProps) {
  const initState: unknown = useLoaderData();
  if (!isSearchState(initState)) {
    throw new Error("Not a SearchState");
  }
  const initDateStart = toDateStr(initState.filters.dateStart);
  const initDateEnd = toDateStr(initState.filters.dateEnd);
  const [dateStart, setDateStart] = useState<string>(initDateStart);
  const [dateEnd, setDateEnd] = useState<string>(initDateEnd);

  useEffect(() => {
    const dateStartParam = searchParams.get("dateStart");
    const dateEndParam = searchParams.get("dateEnd");
    if (dateStartParam) {
      setDateStart(dateStartParam);
    }
    if (dateEndParam) {
      setDateEnd(dateEndParam);
    }
  }, []);

<<<<<<< HEAD
  useEffect(() => {
    handleDate(toDateObj(dateStart), toDateObj(dateEnd))
  }, [dateStart, dateEnd])
=======
  const dateStartRef = useRef<HTMLInputElement>(null);
>>>>>>> main

  return (
    <fieldset className={styles["DateSelect"]} aria-labelledby="date-legend">
      <legend className='sr-only' id="date-legend">Filter by Date</legend>
      <div className={styles["datepickers-wrapper"]}>
        <input
          type="date"
          id="start"
          ref={dateStartRef}
          value={dateStart}
          onChange={(e) => {
            setDateStart(e.currentTarget.value)
            e.target.blur()
          }}
        />
        <p>–</p>
        <input
          type="date"
          id="end"
          value={dateEnd}
          onChange={(e) => {
            setDateEnd(e.currentTarget.value)
            e.target.blur()
          }}
        />
        <button
          aria-label="Clear start date filter"
          onClick={() => {
            setDateStart("");
            setDateEnd("");
          }}
        >
          {'\u00d7'}
        </button>
      </div>
    </fieldset>
  );
}
