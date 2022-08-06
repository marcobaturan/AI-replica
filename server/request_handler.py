from http.server import BaseHTTPRequestHandler
import json
import mimetypes
import os.path
import requests
import urllib.parse as url_parse
from ai_replica.common import get_answer
from server.read_config import config
import server.data_access as data_access

STATIC_FILES_DIR = config['server']['static_files_dir']
BOT_ENGINE = config['bot_engine']
RASA_REST_WEBHOOK = config['rasa']['rest_webhook']
ANONYMOUS_USER_ID = config['server']['anonymous_user_id']

class RequestHandler(BaseHTTPRequestHandler):
  user_id = ANONYMOUS_USER_ID

  def do_GET(self):
    print(f"GET method is called: {self.path}")

    parsed_path = url_parse.urlparse(self.path)
    path = parsed_path.path
    query = url_parse.parse_qs(parsed_path.query)
    if query.get("user"):
      self.user_id = query.get("user")
      
    if (path == "/"):
      path = "/index.html"

    last_slash_index = path.rfind("/")
    resource_name = path if last_slash_index == -1 else path[(last_slash_index + 1):]

    last_dot_index = resource_name.rfind(".")
    resource_extension = ""
    if (last_dot_index != -1):
      resource_extension = resource_name[(last_dot_index + 1):]

    content = None
    content_type = ""
    if (resource_extension != ""):
      file_path = f"{STATIC_FILES_DIR}{path}"
      if (os.path.exists(file_path)):
        with open(file_path, "rb") as f:
          content = f.read()
          content_type = mimetypes.guess_type(path)[0]
    else:
      content = self.__get_api_get_response()
      content_type = "application/json"

    if (content_type != ""):
      self.send_response(200)
    else:
      self.send_response(404)
    self.send_header("Content-type", content_type)
    self.end_headers()
    
    if content:
      self.wfile.write(content)

  def do_POST(self):
    print(f"POST method is called: {self.path}")
    content_type = "application/json"
    content = self.__get_api_post_response()
    data_access.add_message(content, self.user_id)

    self.send_response(200)
    self.send_header("Content-type", content_type)
    self.end_headers()

    self.wfile.write(content.encode("utf8"))

  def __get_api_get_response(self):
    return json.dumps({"message": "Hello, World! I am Bot!"})

  # Currently, get_answer is the default processed action.
  # Other actions can be added later.
  # TODO: Basically a simple router should be implemented to select actions based on request path.
  def __get_api_post_response(self):
    length = int(self.headers.get('content-length'))
    data = self.rfile.read(length)
    obj = json.loads(data)
    user_message = obj["message"]

    # TODO: provide engine logic via a strategy, e.g. implement a separate class/function to process Rasa requests
    if (BOT_ENGINE == "rasa"):
      url = RASA_REST_WEBHOOK
      # the value of the sender field corresponds to the conversation id in rasa conversation store
      data = {
        "sender": self.user_id, # TODO: add user management logic: authentification, etc.
        "message": user_message,
      }
      response = requests.post(url, data = json.dumps(data))
      print(f"rasa resp: {response.text}")
      bot_answers = self.__get_bot_answers_from_rasa_bot_answers(response.text)
    else:        
      bot_answers = [get_answer(user_message)]

    return json.dumps({"messages": bot_answers})

  # TODO: messages sent to client should have a richer format, i.e. not only text should be accepted
  # Images, links, videos, text formatting, etc.
  # Take into account different possible channels: custom web-chat, WhatsApp, Messenger, Telegram, custom Android chat, etc...
  # Different message formatters should be used depending on the channel
  # TODO: move message processing logic out of the web server - to the bot engine
  def __get_bot_answers_from_rasa_bot_answers(self, response_text):
    rasa_bot_answers = json.loads(response_text)
    if (len(rasa_bot_answers) == 0):
      return [[{"type": "text", "content" : "Sorry, I have no answer :("}]]
  
    bot_answers = []    
    for rasa_bot_answer in rasa_bot_answers:
      if (rasa_bot_answer.get("text") != None):
        bot_answers.append([{"type": "text", "content":rasa_bot_answer["text"]}])
      elif (rasa_bot_answer.get("image") != None):
        bot_answers.append([{"type": "image", "content": rasa_bot_answer["image"]}])
      elif (rasa_bot_answer.get("custom") != None):
        bot_answers.append(rasa_bot_answer["custom"])

    return bot_answers
