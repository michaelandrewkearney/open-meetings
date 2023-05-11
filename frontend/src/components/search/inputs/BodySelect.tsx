import { Fragment } from "react";
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
      id={styles["body-select"]}
      aria-labelledby="body-legend"
      role="radiogroup"
      aria-label="Filter by Body"
    >
      <input
        type="radio"
        name="body-select"
        id="all-bodies"
        value="all"
        checked={selectedBody === null}
        onChange={() => handleBodySelect(null)}
      />
      <label htmlFor={"all-bodies"}>
        <span className={styles["body-count"]} aria-hidden="true">
          {numResults}
        </span>
        <div className={styles["body-name"]} role="presentation">
          All bodies
          <span className="sr-only">- {numResults} results</span>
        </div>
      </label>

      {bodyNames ? (
        bodyNames.map((body: string) => {
          return (
            <Fragment key={body}>
              <input
                name="body-select"
                type="radio"
                id={body}
                value={body}
                checked={selectedBody === body}
                aria-required="true"
                onChange={(e) => handleBodySelect(e.currentTarget.value)}
              />
              <label htmlFor={body} key={`${body}-label`}>
                <div className={styles["body-count"]} aria-hidden="true">
                  {facetMap.get(body)}
                </div>
                <div className={styles["body-name"]} role="presentation">
                  {body}
                  <span className="sr-only" key={`${body}-label-name-sr-only`}>
                    - {facetMap.get(body)} results
                  </span>
                </div>
              </label>
            </Fragment>
          );
        })
      ) : (
        <></>
      )}
    </fieldset>
  );
}
