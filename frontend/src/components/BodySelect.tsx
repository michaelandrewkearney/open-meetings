import styles from "./BodySelect.module.css";

import { useEffect, useState } from "react";

interface BodySelectProps {
  /** Map of body names to facet counts */
  facetMap: Map<string, number>;
  handleBodySelect: (body: string | null) => void;
}

export default function BodySelect({
  facetMap,
  handleBodySelect,
}: BodySelectProps) {
  // when checkedBody is null, check "All bodies" option
  const [checkedBody, setCheckedBody] = useState<string | null>(null);

  useEffect(() => {
    handleBodySelect(checkedBody);
  }, [checkedBody]);

  const bodyNames: readonly string[] = [...facetMap.keys()];
  const numResults: number = [...facetMap.values()].reduce(
    (sum, count) => sum + count,
    0
  );
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

      {bodyNames.map((body: string) => {
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
              <span className={styles["body-count"]}>{facetMap.get(body)}</span>
            </label>
          </div>
        );
      })}
    </fieldset>
  );
}
