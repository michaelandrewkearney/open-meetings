import styles from "./BodySelect.module.css";

import { useEffect, useState } from "react";

interface BodySelectProps {
  /** Map of body names to facet counts */
  facetMap: Map<string, number>;
  handleBodySelect: (body: string | null) => void;
  searchParams: URLSearchParams;
}

export default function BodySelect({
  facetMap,
  handleBodySelect,
  searchParams,
}: BodySelectProps) {
  // when checkedBody is null, check "All bodies" option
  const [checkedBody, setCheckedBody] = useState<string | null>(null);
  const [bodyNames, setBodyNames] = useState<readonly string[]>();
  const [numResults, setNumResults] = useState<number>();

  useEffect(() => {
    const bodyParam = searchParams.get("body");
    setCheckedBody(bodyParam === "all" ? null : bodyParam);
  }, []);

  useEffect(() => {
    handleBodySelect(checkedBody);
  }, [checkedBody]);

  useEffect(() => {
    setBodyNames(() => [...facetMap.keys()]);
    const newNumResults: number = [...facetMap.values()].reduce(
      (sum, count) => sum + count,
      0
    );
    setNumResults(() => newNumResults);
  }, [facetMap]);

  return (
    <fieldset className={styles["BodySelect"]}>
      <legend>Body</legend>
      <div className={styles["body-option"]}>
        <input
          type="radio"
          id="all-bodies"
          value="all"
          checked={checkedBody === null}
          onChange={() => setCheckedBody(null)}
        />
        <label htmlFor={"all-bodies"}>
          All Bodies <span className={styles["body-count"]}>{numResults}</span>
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
                checked={checkedBody === body}
                onChange={(e) => setCheckedBody(e.currentTarget.value)}
              />
              <label htmlFor={body}>
                {body}{" "}
                <span className={styles["body-count"]}>
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
