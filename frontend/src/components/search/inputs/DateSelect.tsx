import { useLoaderData } from "react-router-dom";
import { toDateObj, toDateStr } from "../date_utils";
import styles from "./DateSelect.module.css";
import { useEffect, useState } from "react";
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

  return (
    <fieldset className={styles["DateSelect"]} aria-labelledby="date-legend">
      <legend id="date-legend">Filter by Date</legend>
      <div>
        <label htmlFor="start">Start Date</label>
        <input
          type="date"
          id="start"
          value={dateStart}
          onChange={(e) => setDateStart(e.currentTarget.value)}
          onBlur={() => handleDate(toDateObj(dateStart), toDateObj(dateEnd))}
        />
        <button
          onClick={() => {
            setDateStart("");
            handleDate(null, toDateObj(dateEnd));
          }}
          aria-label="Clear start date filter"
        >
          Clear
        </button>

        <label htmlFor="end">End Date</label>
        <input
          type="date"
          id="end"
          value={dateEnd}
          onChange={(e) => setDateEnd(e.currentTarget.value)}
          onBlur={() => handleDate(toDateObj(dateStart), toDateObj(dateEnd))}
        />
        <button
          aria-label="Clear start date filter"
          onClick={() => {
            setDateEnd("");
            handleDate(toDateObj(dateStart), null);
          }}
        >
          Clear
        </button>
      </div>
    </fieldset>
  );
}
