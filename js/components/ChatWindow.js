const { ref, watch, nextTick } = Vue;

export default {
  name: "ChatWindow",
  props: {
    messages: { type: Array, required: true },
  },
  setup(props) {
    const scrollArea = ref(null);

    const scrollToBottom = () => {
      nextTick(() => {
        if (scrollArea.value) {
          scrollArea.value.scrollTop = scrollArea.value.scrollHeight;
        }
      });
    };

    watch(() => props.messages.length, scrollToBottom);

    return { scrollArea };
  },
  template: `
    <div ref="scrollArea" class="chat-window scrollbar-hide">
      <transition-group name="msg">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-row"
          :class="msg.sender === 'Me' ? 'message-row--sent' : 'message-row--received'"
        >
          <div class="message" :class="msg.sender === 'Me' ? 'message--sent' : 'message--received'">
            <span v-if="msg.sender !== 'Me'" class="message__sender">سرور</span>
            <p class="message__text">{{ msg.text }}</p>
          </div>
        </div>
      </transition-group>
    </div>
  `,
};
