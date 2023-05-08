export default async function fetchJson(url: URL): Promise<any> {
  const json = await fetch(url)
    .then((response: Response) => response.json())
    .then((json: any) => json)
    .catch((problem) => {
      return {
        result: "error_connection_refused",
        msg: `Unable to connect to server. Try again later.`,
      };
    });
  return json;
}