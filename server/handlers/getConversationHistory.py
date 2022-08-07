from http.server import BaseHTTPRequestHandler
import json
from server.constants import CONTENT_TYPES
import server.data_access as data_access

def getConversationHistory(request_handler: BaseHTTPRequestHandler, context):
  messages = data_access.get_conversation_messages(context["conversation_id"])

  return {
    "content": json.dumps(messages),
    "content_type": CONTENT_TYPES.APPLICATION_JSON
  }
