import { useLoaderData } from "react-router-dom";
import { toDateObj, toDateStr } from "../date_utils";
import styles from "./DateSelect.module.css";
import {
  KeyboardEvent,
  Ref,
  RefObject,
  useEffect,
  useRef,
  useState,
} from "react";
import { isSearchState } from "../../..";

interface DateSelectProps {
  handleDate: (startDate: Date | null, endDate: Date | null) => void;
}

export default function DateSelect({ handleDate }: DateSelectProps) {
  const initState: unknown = useLoaderData();
  if (!isSearchState(initState)) {
    throw new Error("Not a SearchState");
  }
  const initDateStart = toDateStr(initState.filters.dateStart);
  const initDateEnd = toDateStr(initState.filters.dateEnd);
  const [dateStart, setDateStart] = useState<string>(initDateStart);
  const [dateEnd, setDateEnd] = useState<string>(initDateEnd);

  const startInputRef = useRef<HTMLInputElement>(null);
  const endInputRef = useRef<HTMLInputElement>(null);

  const submitDate = () => {
    handleDate(toDateObj(dateStart, false), toDateObj(dateEnd, true));
  };

  const handleEnterKeydown = (
    e: React.KeyboardEvent<HTMLInputElement>,
    inputRef: RefObject<HTMLInputElement>
  ) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitDate();
      inputRef.current?.blur();
    }
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
      }}
    >
      <fieldset className={styles["DateSelect"]} aria-labelledby="date-legend">
        <legend className="sr-only" id="date-legend">
          Filter by Date
        </legend>
        <div className={styles["datepickers-wrapper"]}>
          <input
            type="date"
            id="start"
            aria-label="Start date"
            value={dateStart}
            ref={startInputRef}
            onChange={(e) => {
              console.log("set start date");
              setDateStart(e.currentTarget.value);
            }}
            onKeyDown={(e) => handleEnterKeydown(e, startInputRef)}
            onSubmit={(e) => console.log("submitted")}
            onBlur={() => submitDate()}
          />

          <span>—</span>
          <input
            type="date"
            id="end"
            value={dateEnd}
            aria-label="End Date"
            ref={endInputRef}
            onChange={(e) => {
              setDateEnd(e.currentTarget.value);
            }}
            onBlur={() => submitDate()}
            onKeyDown={(e) => handleEnterKeydown(e, startInputRef)}
          />
          <ClearButton
            handleClear={() => {
              setDateStart("");
              setDateEnd("");
              handleDate(null, null);
            }}
            ariaLabel="Clear end date"
          />
        </div>
      </fieldset>
    </form>
  );
}

interface ClearButtonProps {
  handleClear: () => void;
  ariaLabel: string;
}

const ClearButton = ({ handleClear, ariaLabel }: ClearButtonProps) => (
  <button
    aria-label={ariaLabel}
    onClick={() => {
      handleClear();
    }}
  >
    {"\u00d7"}
  </button>
);
