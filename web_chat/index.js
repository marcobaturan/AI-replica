const onWindowLoad =  async (event) => {
  console.log('onWindowLoad')
  const userAndBotIdsResponse = await fetch("/getUserAndBotIds", {method: "GET"})
    .then((resp) => resp.json());
  const userId = userAndBotIdsResponse.user_id;
  const botId = userAndBotIdsResponse.bot_id;
  const response = await fetch("/getConversationHistory", {
    method: 'GET', 
  })
    .then((resp) => resp.json());
  console.log("conversation history", userAndBotIdsResponse, response)
  response.forEach((utterance) => {
    if (utterance.user_id === userId) {
      const userMessage = [{"type": "text", "content": utterance.text}];
          
      addMessage(messages, userMessage, "You", "user-message");
    } else if (utterance.user_id === botId) {
      const botResponse = JSON.parse(utterance.text);
      const botMessages = botResponse.messages || [];
      botMessages.forEach((message) => {
        addMessage(messages, message, currentBot.name, "bot-message");
      });
    }
  })
};
window.addEventListener('load', onWindowLoad);

const sendMessageButton = document.getElementById("sendMessageButton");
sendMessageButton.addEventListener("click", onSendMessageButtonClicked);

const messages = document.getElementById("messages");
// TODO: retrieve info about registered bots from the server and provide a user possibility to choose a bot with whom to talk
const currentBot = {
  name: "Ben",
};

const messageInput = document.getElementById("messageInput");

const botInfo = document.getElementById("botInfo");
botInfo.innerHTML = `Hello, I am ${currentBot.name}.`;

async function onSendMessageButtonClicked(event) {
  const userMessage = [{"type": "text", "content": messageInput.value}];
  messageInput.value = "";

  const addedMessage = addMessage(messages, userMessage, "You", "user-message");
  addedMessage.scrollIntoView(false);

  // TODO: for now, send only text messages to the server
  // Think how to add images and links to be processed by the server/bot.
  const requestData = { message: userMessage[0].content };
  const response = await fetch("/getResponse", {
    method: 'POST', 
    body: JSON.stringify(requestData),
  });
  const botResponse = await response.json();
  const botMessages = botResponse.messages || [];
  botMessages.forEach((message) => {
    const addedMessage = addMessage(messages, message, currentBot.name, "bot-message");
    addedMessage.scrollIntoView(false);
  });
}

function addMessage(messagesElement, messageParts, userName, modifier) {
  const messageElement = document.createElement("article");
  messageElement.className = `message message_${modifier}`;
  let messageHtml = `<section class="message-name">${userName}: </section>`;
  messageHtml += '<section>';
  messageParts.forEach((messagePart) => {
    switch (messagePart.type) {
      case "text":
        messageHtml += messagePart.content;
        break;
      case "image":
        messageHtml += `<img class="message__image" src='${messagePart.content}' />`;
        break;
      case "link":
        messageHtml += `<a href='${messagePart.link}' target='blank'>${messagePart.text}</a>`;
        break;
    }
  });

  messageHtml += '</section>';
  messageElement.innerHTML = messageHtml;
  messagesElement.appendChild(messageElement);

  return messageElement;
}
