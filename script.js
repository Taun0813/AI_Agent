const messageInput = document.querySelector("#message-input");
const chatbody = document.querySelector(".chat-body");
const sendMessageButton = document.querySelector("#send-message");
const fileInput = document.querySelector("#file-input");
const fileUploadWrapper = document.querySelector(".file-upload-wrapper");
const fileCancelButton = document.querySelector("#file-cancel");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");

// API setup
// const API_KEY = "AIzaSyCwH5Ns0O5uVKElBPE1ulbZSvuE_tgIPxw";
// const API_URL = `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${API_KEY}`;
// const userData = {
//   message: null,
//   file: {
//     data: null,
//     mime_type: null,
//   },
// };
const API_URL = "http://localhost:8000/chat"; // Đổi sang endpoint Flask
const userData = {
  message: null,
  file: {
    data: null,
    mime_type: null,
  },
};

const chatHistory = [];

const innitialInputHeight = messageInput.scrollHeight;

// Create message element with dynamic classes and return it
const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

// Hiệu ứng Scroll
function smoothScrollToBottom(duration = 800) {
  const start = chatbody.scrollTop;
  const end = chatbody.scrollHeight;
  const distance = end - start;
  const startTime = performance.now();

  function scroll(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1); // 0 → 1

    // easeInOutQuad easing function
    const ease =
      progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;

    chatbody.scrollTop = start + distance * ease;

    if (progress < 1) {
      requestAnimationFrame(scroll);
    }
  }

  requestAnimationFrame(scroll);
}

// Generate bot response using API
const generateBotResponse = async (incomingMessageDiv) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  // Add user message to chat history (nếu cần lưu lịch sử phía FE)
  chatHistory.push({
    role: "user",
    message: userData.message,
    ...(userData.file.data ? { file: userData.file } : {}),
  });

  // API request options
  const formData = new FormData();
  formData.append("message", userData.message);
  if (userData.file.data) {
    // Nếu backend hỗ trợ file, gửi file dạng base64 hoặc file object
    formData.append("file", userData.file.data);
    formData.append("mime_type", userData.file.mime_type);
  }

  try {
    // Fetch bot response from Flask API
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userData.message }), // Đúng trường
    };
    const response = await fetch(API_URL, requestOptions);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Server error");

    // Hiển thị phản hồi từ backend
    let botReply = data.response || "Không có phản hồi";

    function cleanBotReply(text) {
      // Loại bỏ đoạn đầu (prompt/hướng dẫn)
      text = text.replace(
        /Bạn là nhân viên tư vấn bán hàng điện thoại[^]*?\n/i,
        ""
      );
      // Loại bỏ đoạn cuối (hướng dẫn hoặc lặp lại yêu cầu)
      text = text.replace(
        /Hãy giới thiệu lý do nổi bật[^]*?(Khách hàng:.*)?$/i,
        ""
      );
      return text.trim();
    }

    botReply = cleanBotReply(botReply);

    // Nếu model trả về cả prompt, tách lấy phần trả lời sau hướng dẫn
    const splitIndex = botReply.lastIndexOf('Ví dụ cách trả lời:');
    if (splitIndex !== -1) {
      botReply = botReply.slice(splitIndex + 'Ví dụ cách trả lời:'.length).trim();
      if (botReply.startsWith('"') && botReply.endsWith('"')) {
        botReply = botReply.slice(1, -1);
      }
    }

    // Format lại cho đẹp: các dòng bắt đầu bằng "-" thành danh sách, còn lại là đoạn văn
    function formatBotReply(text) {
      // Tách các dòng
      const lines = text.split('\n').map(line => line.trim()).filter(Boolean);
      let html = '';
      let inList = false;
      lines.forEach(line => {
        if (line.startsWith('-')) {
          if (!inList) {
            html += '<ul>';
            inList = true;
          }
          // Bôi đậm tên sản phẩm nếu có dạng "- tên (thông tin)"
          const match = line.match(/^- ([^()]+)(.*)$/);
          if (match) {
            html += `<li><strong>${match[1].trim()}</strong>${match[2]}</li>`;
          } else {
            html += `<li>${line.slice(1).trim()}</li>`;
          }
        } else {
          if (inList) {
            html += '</ul>';
            inList = false;
          }
          html += `<p>${line}</p>`;
        }
      });
      if (inList) html += '</ul>';
      return html;
    }

    messageElement.innerHTML = formatBotReply(botReply);
    // Lưu lịch sử nếu cần
    chatHistory.push({
      role: "model",
      message: data.response,
    });
  } catch (error) {
    console.log(error);
    messageElement.innerText = error.message;
    messageElement.style.color = "#ff0000";
  } finally {
    userData.file = {};
    incomingMessageDiv.classList.remove("thinking");
    smoothScrollToBottom(800);
  }
};

// Hanalde outgoing user messages
const handleOutgoingMessage = (e) => {
  e.preventDefault();
  userData.message = messageInput.value.trim();
  messageInput.value = "";
  fileUploadWrapper.classList.remove("file-uploaded");
  messageInput.dispatchEvent(new Event("input"));

  // Create and display user message
  const messageContent = `<div class="message-text"></div>
  ${
    userData.file.data
      ? `<img src="data:${userData.file.mime_type};base64,${userData.file.data}"  class="attachment" />`
      : ""
  }`;
  const outgoingMessageDiv = createMessageElement(
    messageContent,
    "user-message"
  );

  outgoingMessageDiv.querySelector(".message-text").textContent =
    userData.message;
  chatbody.appendChild(outgoingMessageDiv);
  smoothScrollToBottom(800);

  // simulate bot response with thinking indicator after a delay
  setTimeout(() => {
    const messageContent = `  <svg
            class="bot-avatar"
            xmlns="http://www.w3.org/2000/svg"
            width="50"
            height="50"
            viewBox="0 0 1024 1024"
          >
            <path
              d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9zM351.7 448.2c0-29.5 23.9-53.5 53.5-53.5s53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5-53.5-23.9-53.5-53.5zm157.9 267.1c-67.8 0-123.8-47.5-132.3-109h264.6c-8.6 61.5-64.5 109-132.3 109zm110-213.7c-29.5 0-53.5-23.9-53.5-53.5s23.9-53.5 53.5-53.5 53.5 23.9 53.5 53.5-23.9 53.5-53.5 53.5zM867.2 644.5V453.1h26.5c19.4 0 35.1 15.7 35.1 35.1v121.1c0 19.4-15.7 35.1-35.1 35.1h-26.5zM95.2 609.4V488.2c0-19.4 15.7-35.1 35.1-35.1h26.5v191.3h-26.5c-19.4 0-35.1-15.7-35.1-35.1zM561.5 149.6c0 23.4-15.6 43.3-36.9 49.7v44.9h-30v-44.9c-21.4-6.5-36.9-26.3-36.9-49.7 0-28.6 23.3-51.9 51.9-51.9s51.9 23.3 51.9 51.9z"
            ></path>
          </svg>
          <div class="message-text">
            <div class="thinking-indicator">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>`;
    const incomingMessageDiv = createMessageElement(
      messageContent,
      "bot-message",
      "thinking"
    );
    chatbody.appendChild(incomingMessageDiv);
    smoothScrollToBottom(800);
    generateBotResponse(incomingMessageDiv);
  }, 600);
};

// Handle Enter key press for sending messages
messageInput.addEventListener("keydown", (e) => {
  const userMessage = e.target.value.trim();
  if (
    e.key === "Enter" &&
    userMessage &&
    !e.shiftKey &&
    window.innerWidth > 768
  ) {
    handleOutgoingMessage(e);
  }
});

// Adjust input field height dynamically
messageInput.addEventListener("input", () => {
  messageInput.style.height = `${innitialInputHeight}px`;
  messageInput.style.height = `${messageInput.scrollHeight}px`;
  document.querySelector(".chat-form").style.borderRadius =
    messageInput.scrollHeight > innitialInputHeight ? "15px" : "32px";
});

// handle file input change
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    fileUploadWrapper.querySelector("img").src = e.target.result;
    fileUploadWrapper.classList.add("file-uploaded");
    const base64String = e.target.result.split(",")[1];

    // Store filedata vao trong userData
    userData.file = {
      data: base64String,
      mime_type: file.type,
    };

    fileInput.value = "";
  };

  reader.readAsDataURL(file);
});

// Cancel file upload
fileCancelButton.addEventListener("click", () => {
  userData.file = {};
  fileUploadWrapper.classList.remove("file-uploaded");
});

// Initialize emoji picker and handle emoji selection
const picker = new EmojiMart.Picker({
  theme: "light",
  skinTonePosition: "none",
  previewPosition: "none",
  onEmojiSelect: (emoji) => {
    const { selectionStart: start, selectionEnd: end } = messageInput;
    messageInput.setRangeText(emoji.native, start, end, "end");
    messageInput.focus();
  },
  onClickOutside: (e) => {
    if (e.target.id === "emoji-picker") {
      document.body.classList.toggle("show-emoji-picker");
    } else {
      document.body.classList.remove("show-emoji-picker");
    }
  },
});

document.querySelector(".chat-form").appendChild(picker);

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e));
document
  .querySelector("#file-upload")
  .addEventListener("click", () => fileInput.click());

chatbotToggler.addEventListener("click", () =>
  document.body.classList.toggle("show-chatbot")
);

closeChatbot.addEventListener("click", () =>
  document.body.classList.remove("show-chatbot")
);
