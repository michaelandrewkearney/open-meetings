import styles from "./BodySelect.module.css";

import { useEffect, useState } from "react";

interface BodySelectProps {
  /** Map of body names to facet counts */
  facetMap: Map<string, number>;
  selectedBody: string | null;
  handleBodySelect: (body: string | null) => void;
  searchParams: URLSearchParams;
}

export default function BodySelect({
  facetMap,
  selectedBody,
  handleBodySelect,
  searchParams,
}: BodySelectProps) {
  const bodyNames = [...facetMap.keys()];
  const numResults: number = [...facetMap.values()].reduce(
    (sum, count) => sum + count,
    0
  );
  const selectedOption = selectedBody === null ? "all" : selectedBody;

  return (
    <fieldset className={styles["BodySelect"]} aria-labelledby="body-legend">
      <legend id="body-legend">Filter by Body</legend>
      <div className={styles["body-option"]}>
        <input
          type="radio"
          id="all-bodies"
          value="all"
          checked={selectedOption === "all"}
          onChange={() => handleBodySelect(null)}
        />
        <label htmlFor={"all-bodies"}>
          All Bodies <span className="sr-only">{numResults} results</span>
          <span className={styles["body-count"]} aria-hidden="true">
            {numResults}
          </span>
        </label>
      </div>

      {bodyNames ? (
        bodyNames.map((body: string) => {
          return (
            <div className={styles["body-option"]} key={body}>
              <input
                type="radio"
                id={body}
                value={body}
                checked={selectedBody === body}
                onChange={(e) => handleBodySelect(e.currentTarget.value)}
              />
              <label htmlFor={body}>
                <span role="presentation">
                  {body}
                  <span className="sr-only">
                    : {facetMap.get(body)} results
                  </span>{" "}
                </span>
                <span className={styles["body-count"]} aria-hidden="true">
                  {facetMap.get(body)}
                </span>
              </label>
            </div>
          );
        })
      ) : (
        <></>
      )}
    </fieldset>
  );
}
