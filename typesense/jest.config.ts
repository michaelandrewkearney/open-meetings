import type {Config} from 'jest';

const config: Config = {
  preset: "ts-jest",
  globalSetup: "./src/tests/setup.ts",
  globalTeardown: "./src/tests/teardown.ts",
  globals: {
    __SERVER_PROCESS__: null
  }
};

export default config;