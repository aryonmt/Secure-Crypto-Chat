/**
 * BridgeClient
 *
 * Thin wrapper around the native WebSocket connecting the browser to the
 * local Python bridge (bridge.py). It knows nothing about Vue or the DOM —
 * it only translates raw WebSocket frames into plain callbacks, so it can
 * be tested or reused independently of the UI layer.
 */
export class BridgeClient {
  /**
   * @param {Object} handlers
   * @param {() => void} handlers.onConnected - bridge confirmed the TCP/SSL connection.
   * @param {(msg: {sender: string, text: string}) => void} handlers.onMessage - chat message from the server.
   * @param {(rawPayload: string) => void} handlers.onSniffer - raw payload that was just sent on the wire.
   * @param {(message: string) => void} handlers.onServerError - the bridge/backend reported an error.
   * @param {(message: string) => void} handlers.onSocketError - the WebSocket connection itself failed.
   */
  constructor({ onConnected, onMessage, onSniffer, onServerError, onSocketError } = {}) {
    this.socket = null;
    this.onConnected = onConnected ?? (() => {});
    this.onMessage = onMessage ?? (() => {});
    this.onSniffer = onSniffer ?? (() => {});
    this.onServerError = onServerError ?? (() => {});
    this.onSocketError = onSocketError ?? (() => {});
  }

  /**
   * Open the WebSocket and, once open, send the connection config so the
   * bridge can initialize the underlying TCP/SSL backend.
   * @param {string} bridgeUrl
   * @param {Object} config
   */
  connect(bridgeUrl, config) {
    this.socket = new WebSocket(bridgeUrl);

    this.socket.onopen = () => {
      this.socket.send(JSON.stringify(config));
    };

    this.socket.onmessage = (event) => this._handleIncoming(event);

    this.socket.onerror = () => {
      this.onSocketError(
        "اتصال به Bridge محلی (ws://localhost:8765) شکست خورد. آیا bridge.py در حال اجراست؟"
      );
    };
  }

  /** @private */
  _handleIncoming(event) {
    const data = JSON.parse(event.data);

    switch (data.type) {
      case "status":
        if (data.msg === "connected") this.onConnected();
        break;
      case "message":
        this.onMessage({ sender: data.sender, text: data.text });
        break;
      case "sniffer":
        this.onSniffer(data.raw_payload);
        break;
      case "error":
        this.onServerError(data.msg);
        break;
      default:
        console.warn("Unknown bridge message type:", data.type);
    }
  }

  /**
   * Send a chat message to be encrypted/forwarded by the bridge.
   * @param {string} text
   */
  sendChat(text) {
    this.socket?.send(JSON.stringify({ type: "send_chat", text }));
  }

  /** Close the connection, if any. Safe to call multiple times. */
  disconnect() {
    this.socket?.close();
    this.socket = null;
  }
}
