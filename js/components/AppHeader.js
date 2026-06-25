const { computed } = Vue;

export default {
  name: "AppHeader",
  props: {
    isConnected: { type: Boolean, default: false },
    mode: { type: String, default: "" },
  },
  emits: ["disconnect"],
  setup(props) {
    const isSecure = computed(() => props.mode === "ssl");
    const dotClass = computed(() => (isSecure.value ? "status-dot--secure" : "status-dot--weak"));

    return { dotClass };
  },
  template: `
    <header class="app-header">
      <h1 class="app-header__title">
        <svg class="app-header__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
          <path d="M9.5 12l1.8 1.8 3.2-3.6" />
        </svg>
        پیام‌رسان امن و رمزنگاری‌شده
      </h1>

      <div v-if="isConnected" class="app-header__status">
        <span class="app-header__badge">
          <span class="status-dot" :class="dotClass"></span>
          {{ mode.toUpperCase() }} MODE
        </span>
        <button class="btn btn--ghost-danger" @click="$emit('disconnect')">
          قطع ارتباط
        </button>
      </div>
    </header>
  `,
};
