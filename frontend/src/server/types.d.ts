
/**
 * Function that fetches a JSON given a URL. Allows for mocking API responses.
 */
export interface RequestJsonFunction {
  (url: URL): Promise<any>;
}