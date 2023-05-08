import { toDateObj } from "../date_utils";
import styles from "./DateSelect.module.css";
import { useEffect, useState } from "react";

interface DateSelectProps {
  handleDate: (startDate: Date | null, endDate: Date | null) => void;
  searchParams: URLSearchParams;
}

export default function DateSelect({
  handleDate,
  searchParams,
}: DateSelectProps) {
  const [dateStart, setDateStart] = useState<string>("");
  const [dateEnd, setDateEnd] = useState<string>("");

  useEffect(() => {
    console.log([...searchParams.entries()]);
    const dateStartParam = searchParams.get("dateStart");
    const dateEndParam = searchParams.get("dateEnd");
    if (dateStartParam) {
      setDateStart(dateStartParam);
    }
    if (dateEndParam) {
      setDateEnd(dateEndParam);
    }
    handleDate(
      dateStartParam ? toDateObj(dateStartParam) : null,
      dateEndParam ? toDateObj(dateEndParam) : null
    );
  }, []);

  useEffect(() => {
    console.log(dateStart);
  }, [dateStart]);

  return (
    <fieldset className={styles["DateSelect"]}>
      <legend>Date</legend>
      <div>
        <label htmlFor="start">Start</label>
        <input
          type="date"
          id="start"
          value={dateStart}
          required
          onChange={(e) => setDateStart(e.currentTarget.value)}
          onBlur={() => handleDate(toDateObj(dateStart), toDateObj(dateEnd))}
        />
        <button
          onClick={() => {
            setDateStart("");
            handleDate(null, toDateObj(dateEnd));
          }}
        >
          Clear
        </button>

        <label htmlFor="end">End</label>
        <input
          type="date"
          id="end"
          value={dateEnd}
          required
          pattern="\d{4}-\d{2}-\d{2}"
          onChange={(e) => setDateEnd(e.currentTarget.value)}
          onBlur={() => handleDate(toDateObj(dateStart), toDateObj(dateEnd))}
        />
        <button
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
