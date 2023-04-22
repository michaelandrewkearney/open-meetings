import { FormEvent, useEffect, useState } from "react";

interface BodySelectProps {
  facetMap: Map<string, number>;
  handleBodySelect: (body: string | null) => void;
}

export default function BodySelect({
  facetMap,
  handleBodySelect,
}: BodySelectProps) {
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
    <form>
      <fieldset>
        <legend>Body</legend>
        <input
          type="radio"
          id="all-bodies"
          value="all"
          checked={checkedBody === null}
          onChange={() => setCheckedBody(null)}
        />
        <label htmlFor={"all-bodies"}>All Bodies | {numResults}</label>
        {bodyNames.map((body: string) => {
          return (
            <div key={body}>
              <input
                type="radio"
                id={body}
                value={body}
                checked={checkedBody === body}
                onChange={(e) => setCheckedBody(e.currentTarget.value)}
              />
              <label htmlFor={body}>
                {body} | {facetMap.get(body)}
              </label>
            </div>
          );
        })}
      </fieldset>
    </form>
  );
}
