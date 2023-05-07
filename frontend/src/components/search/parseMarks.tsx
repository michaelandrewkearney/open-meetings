export const snippetToJSXElt = (text: string): JSX.Element => {
  const nonMarks: string[] = text.split(/<mark>(.*?)<\/mark>/g);
  let elt: JSX.Element = <></>;
  for (let i = 0; i < nonMarks.length; i++) {
    if (i % 2 === 0) {
      elt = (
        <>
          {elt}
          {nonMarks[i]}
        </>
      );
    } else {
      elt = (
        <>
          {elt}
          <mark>{nonMarks[i]}</mark>
        </>
      );
    }
  }

  return elt;
};
