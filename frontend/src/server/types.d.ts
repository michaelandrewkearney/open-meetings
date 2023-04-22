export interface RequestJsonFunction {
  (url: URL): Promise<any>;
}