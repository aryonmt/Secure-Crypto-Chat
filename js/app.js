const { createApp, reactive, ref, computed, onMounted } = Vue;

import { BRIDGE_URL, createDefaultConfig } from "./config.js";
import { BridgeClient } from "./services/websocketService.js";
import AppHeader from "./components/AppHeader.js";
import ConnectionForm from "./components/ConnectionForm.js";
import ChatWindow from "./components/ChatWindow.js";
import SnifferPanel from "./components/SnifferPanel.js";
import MessageComposer from "./components/MessageComposer.js";

const App = {
  name: "App",
  components: {
    AppHeader,
    ConnectionForm,
    ChatWindow,
    SnifferPanel,
    MessageComposer,
  },
  setup() {
    const isConnected = ref(false);
    const isConnecting = ref(false);
    const errorMessage = ref("");

    const config = reactive(createDefaultConfig());
    const messages = ref([]);
    const snifferLogs = ref([]);

    /** @type {BridgeClient | null} */
    let bridge = null;

    const discoverServerIp = async () => {
      try {
        const response = await fetch("/api/server-info");
        if (response.ok) {
          const data = await response.json();
          if (data.server_ip) {
            config.host = data.server_ip;
          }
        }
      } catch (error) {
        console.error("Failed to auto-discover server IP:", error);
      }
    };

    onMounted(() => {
      discoverServerIp();
    });

    // Drives the top accent bar's color once connected: amber for the
    // classical ciphers, teal for SSL/TLS.
    const accentClass = computed(() => {
      if (!isConnected.value) return "";
      return config.mode === "ssl" ? "app-card--secure" : "app-card--weak";
    });

    // In SSL mode, the real payload is opaque ciphertext; we show a
    // representative TLS-record-looking string instead for visualization.
    const formatSnifferPayload = (rawPayload) => {
      if (config.mode !== "ssl") return rawPayload;
      const noise = Math.random().toString(16).substr(2, 10);
      return `\\x17\\x03\\x03\\x00${noise}\\xfa...`;
    };

    const resetSession = () => {
      bridge?.disconnect();
      bridge = null;
      isConnected.value = false;
      messages.value = [];
      snifferLogs.value = [];
    };

    const connect = () => {
      if (!config.username || !config.host || !config.port) {
        errorMessage.value = "لطفاً تمام فیلدها را پر کنید.";
        return;
      }

      errorMessage.value = "";
      isConnecting.value = true;

      bridge = new BridgeClient({
        onConnected: () => {
          isConnected.value = true;
          isConnecting.value = false;
          messages.value.push({
            sender: "System",
            text: `به سرور ${config.host} متصل شدید.`,
          });
        },
        onMessage: (msg) => messages.value.push(msg),
        onSniffer: (rawPayload) => {
          snifferLogs.value.unshift({
            time: new Date().toLocaleTimeString(),
            payload: formatSnifferPayload(rawPayload),
          });
        },
        onServerError: (msg) => {
          errorMessage.value = msg;
          isConnecting.value = false;
          resetSession();
        },
        onSocketError: (msg) => {
          errorMessage.value = msg;
          isConnecting.value = false;
        },
      });

      bridge.connect(BRIDGE_URL, config);
    };

    const handleSendMessage = (text) => {
      messages.value.push({ sender: "Me", text });
      bridge?.sendChat(text);
    };

    return {
      isConnected,
      isConnecting,
      errorMessage,
      config,
      messages,
      snifferLogs,
      accentClass,
      connect,
      handleSendMessage,
      disconnect: resetSession,
    };
  },
  template: `
    <div class="app-card" :class="accentClass">
      <app-header :is-connected="isConnected" :mode="config.mode" @disconnect="disconnect" />

      <transition name="screen" mode="out-in">
        <connection-form
          v-if="!isConnected"
          key="connection"
          :config="config"
          :is-connecting="isConnecting"
          :error-message="errorMessage"
          @submit="connect"
        />

        <div v-else key="chat" class="chat-screen">
          <chat-window :messages="messages" />
          <sniffer-panel :logs="snifferLogs" :mode="config.mode" />
          <message-composer @send="handleSendMessage" />
        </div>
      </transition>
    </div>
  `,
};

createApp(App).mount("#app");
