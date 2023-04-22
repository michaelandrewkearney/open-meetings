import { ChangeEvent, useEffect, useState } from "react";
import { SearchState } from "../meetingTypes";

interface DateSelectProps {
  handleDate: (startDate: Date | null, endDate: Date | null) => void;
}

export default function DateSelect({ handleDate }: DateSelectProps) {
  /**
   * converts date string in the format 'yyyy-mm-dd' to a Date object
   *
   * @param date
   * @returns
   */
  const toDate = (date: string): Date | null => {
    if (date === "") return null;
    const year: number = parseInt(date.substring(0, 4));
    const month: number = parseInt(date.substring(5, 7)) - 1;
    const day: number = parseInt(date.slice(8));
    return new Date(year, month, day);
  };

  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  return (
    <fieldset>
      <label htmlFor="start">Start date:</label>
      <input
        type="date"
        id="start"
        value={startDate}
        required
        onChange={(e) => setStartDate(e.currentTarget.value)}
        onBlur={() => handleDate(toDate(startDate), toDate(endDate))}
      />

      <label htmlFor="end">End date:</label>
      <input
        type="date"
        id="end"
        value={endDate}
        required
        pattern="\d{4}-\d{2}-\d{2}"
        onChange={(e) => setEndDate(e.currentTarget.value)}
        onBlur={() => handleDate(toDate(startDate), toDate(endDate))}
      />
    </fieldset>
  );
}
