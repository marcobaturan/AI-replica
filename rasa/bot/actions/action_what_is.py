# This action replies on the queries like "Who is <person_name>"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionWhatIs(Action):

  def name(self) -> Text:
    return "action_what_is"

  def run(
    self, 
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

    print("action_what_is is being run")
    entities = tracker.latest_message["entities"]
    name_entity = None
    for entity in entities:
      if entity["entity"] == "name":
        name_entity = entity

    name = name_entity["value"] if name_entity else None
    if name:
      # TODO: return data about requested thing using Wikipedia API
      # TODO: think about how to return formatted text data, including links, to different channels, Web, Android, etc.
      # It looks like a channel-specific formatters should be introduced here.
      message = [
        {"type": "text", "content": f"Try to check about {name} here: "},
        {"type": "link", "text": f"https://en.wikipedia.org/wiki/{name}", "link": f"https://en.wikipedia.org/wiki/{name}"},
        {"type": "text", "content": "."},
      ]      
      dispatcher.utter_message(json_message = message)
    else:
      message = [
        {"type": "text", "content": f"I have no clue about it."},
      ]
      dispatcher.utter_message(json_message = message)

    return []
