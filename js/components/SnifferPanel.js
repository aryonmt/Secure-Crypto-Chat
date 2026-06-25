export default {
  name: "SnifferPanel",
  props: {
    logs: { type: Array, required: true },
    mode: { type: String, default: "" },
  },
  template: `
    <div class="sniffer">
      <div class="sniffer__bar">
        <span>&gt;_ NETWORK_SNIFFER_LOGS</span>
        <span v-if="mode === 'ssl'" class="sniffer__tag">
          <span class="status-dot status-dot--secure"></span>
          ENCRYPTED TUNNEL ACTIVE
        </span>
      </div>
      <div
        v-for="(log, idx) in logs"
        :key="idx"
        class="sniffer__entry"
        :class="mode === 'ssl' ? 'sniffer__entry--secure' : 'sniffer__entry--weak'"
      >
        <span class="sniffer__time">[{{ log.time }}] PAYLOAD: </span>
        <span class="sniffer__payload">{{ log.payload }}</span>
      </div>
    </div>
  `,
};
