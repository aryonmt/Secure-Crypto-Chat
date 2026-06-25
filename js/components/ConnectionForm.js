const MODE_OPTIONS = [
  { value: "caesar", label: "رمزنگاری کلاسیک (سزار)", dot: "weak" },
  { value: "vigenere", label: "رمزنگاری چندالفبایی (ویژنر)", dot: "weak" },
  { value: "ssl", label: "ارتباط فوق‌امن (SSL/TLS)", dot: "secure" },
];

export default {
  name: "ConnectionForm",
  props: {
    // `config` is a single reactive object owned by the parent (App).
    // We mutate its fields directly via v-model below instead of emitting
    // one update event per keystroke per field — Vue allows this for
    // object/array props since we never reassign the prop itself, only
    // its nested properties. The parent still owns and reads the object.
    config: { type: Object, required: true },
    isConnecting: { type: Boolean, default: false },
    errorMessage: { type: String, default: "" },
  },
  emits: ["submit"],
  setup() {
    return { modeOptions: MODE_OPTIONS };
  },
  template: `
    <div class="connection-screen">
      <form class="connection-card" @submit.prevent="$emit('submit')">
        <h2 class="connection-card__title">تنظیمات اتصال</h2>

        <div class="field">
          <label class="field__label">نام کاربری</label>
          <input v-model="config.username" type="text" class="field__input" placeholder="مثلاً: Ali" />
        </div>

        <div class="field-row">
          <div class="field field--grow">
            <label class="field__label">آدرس سرور (Host)</label>
            <input v-model="config.host" type="text" class="field__input" />
          </div>
          <div class="field field--narrow">
            <label class="field__label">پورت</label>
            <input v-model="config.port" type="number" class="field__input" />
          </div>
        </div>

        <div class="field">
          <label class="field__label">لایه امنیتی و رمزنگاری</label>
          <div class="mode-select" role="radiogroup">
            <button
              v-for="opt in modeOptions"
              :key="opt.value"
              type="button"
              class="mode-select__option"
              :class="{ 'mode-select__option--active': config.mode === opt.value }"
              role="radio"
              :aria-checked="config.mode === opt.value"
              @click="config.mode = opt.value"
            >
              <span class="mode-select__dot" :class="'mode-select__dot--' + opt.dot"></span>
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div v-if="config.mode === 'vigenere'" class="field">
          <label class="field__label">کلید خصوصی ویژنر</label>
          <input
            v-model="config.key"
            type="text"
            class="field__input field__input--accent"
            placeholder="NETWORK"
          />
        </div>

        <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>

        <button type="submit" class="btn btn--primary" :disabled="isConnecting">
          {{ isConnecting ? 'در حال اتصال...' : 'ورود به چت‌روم' }}
        </button>
      </form>
    </div>
  `,
};
