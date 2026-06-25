const { ref } = Vue;

export default {
  name: "MessageComposer",
  emits: ["send"],
  setup(props, { emit }) {
    const text = ref("");

    const submit = () => {
      const trimmed = text.value.trim();
      if (!trimmed) return;
      emit("send", trimmed);
      text.value = "";
    };

    return { text, submit };
  },
  template: `
    <div class="composer">
      <input
        v-model="text"
        @keyup.enter="submit"
        type="text"
        class="composer__input"
        placeholder="پیام خود را بنویسید..."
      />
      <button class="composer__send" @click="submit" aria-label="ارسال">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M19 12H5" />
          <path d="M11 6l-6 6 6 6" />
        </svg>
      </button>
    </div>
  `,
};
