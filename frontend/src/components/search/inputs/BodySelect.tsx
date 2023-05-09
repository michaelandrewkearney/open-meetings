import styles from "./BodySelect.module.css";

interface BodySelectProps {
  /** Map of body names to facet counts */
  facetMap: Map<string, number>;
  selectedBody: string | null;
  handleBodySelect: (body: string | null) => void;
}

export default function BodySelect({
  facetMap,
  selectedBody,
  handleBodySelect,
}: BodySelectProps) {
  const bodyNames = [...facetMap.keys()];
  const numResults: number = [...facetMap.values()].reduce(
    (sum, count) => sum + count,
    0
  );

  return (
    <fieldset
      className={styles["BodySelect"]}
      aria-labelledby="body-legend"
      role="radiogroup"
    >
      <legend id="body-legend">Filter by Body</legend>
      <div className={styles["body-option"]}>
        <input
          type="radio"
          name="body-select"
          id="all-bodies"
          value="all"
          checked={selectedBody === null}
          onChange={() => handleBodySelect(null)}
        />
        <label htmlFor={"all-bodies"}>
          All Bodies <span className="sr-only"> - {numResults} results</span>
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
                name="body-select"
                type="radio"
                id={body}
                value={body}
                checked={selectedBody === body}
                aria-required="true"
                onChange={(e) => handleBodySelect(e.currentTarget.value)}
              />
              <label htmlFor={body}>
                <span role="presentation">
                  {body}
                  <span className="sr-only">
                    - {facetMap.get(body)} results
                  </span>
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
