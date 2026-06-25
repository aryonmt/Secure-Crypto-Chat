/**
 * App-wide constants.
 */
export const BRIDGE_URL = "ws://localhost:8765";

/**
 * Returns a fresh default config object for the connection form.
 * A factory function (rather than a shared object literal) avoids
 * accidental cross-instance mutation if this is ever used twice.
 */
export function createDefaultConfig() {
  return {
    username: "Ali",
    host: "127.0.0.1",
    port: 5050,
    mode: "vigenere",
    key: "NETWORK",
  };
}
