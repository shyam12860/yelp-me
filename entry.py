from flask import Flask, request
from wit import Wit
import json
import requests
import os

app = Flask(__name__)

# Wit api start

def first_entity_value(entities, entity):
    """
    Returns first entity value
    """
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

#### This function would be the entry point for whatever we want to do. We add
#### to context and then return the values to the bot, and configure wit ai to
#### output the right thing.
def echo_entities(request):
    context = request['context']
    entities = request['entities']
    #temporary
    query = {}
    query['location'] = first_entity_value(entities, 'location') 
    query['datetime'] = first_entity_value(entities, 'datetime')
    query['cuisine'] = first_entity_value(entities, 'cuisine')
    query['rating'] = first_entity_value(entities, 'rating')
    query['cost'] = first_entity_value(entities, 'cost')
    print "======================================================="
    print query
    # must put try catch statements so that all unacceptable inputs get a
    # proper reply
    if query:
        context['location'] = query 
    return context

def send(request, response):
    send_message(PAT, request['session_id'], response['text'])

actions = {
    'send': send,
    'echo_entities': echo_entities,
}

wit_client = Wit(access_token=os.environ['WIT_TOKEN'], actions=actions)
# Wit api end

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = os.environ['FB_APP_TOKEN']
# Facebook bot start
@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'my_voice_is_my_password_verify_me':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print "Handling Messages"
  payload = request.get_data()
  for sender, message in messaging_events(payload):
    # session_id is just used to send the sender id across
    try:
        wit_client.run_actions(message=message, session_id=sender)
    except Exception as error:
        print str(error)
  return "ok"

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"

def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text
# Facebook bot end
if __name__ == '__main__':
  app.run()
