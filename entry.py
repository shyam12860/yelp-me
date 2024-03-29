from flask import Flask, request
from wit import Wit
from yelpScript import getResults
import json
import requests
import os
from sklearn import tree
prev_result = {}
all_trees = {}
all_data = {}
all_y = {}

app = Flask(__name__)

# Wit api start
def suggest(session_id, results):
    global all_trees
    global all_data
    global all_y

    if session_id in all_trees:
        tree = all_trees[session_id]
        keys = range(1,len(results.keys())+1)
        data = []
        for key in keys:
            num_reviews = results[key]["reviews"]
            rating = results[key]["rating"]
            row = [num_reviews,rating]
            data.append(row)
        predictions = tree.predict(data)
        for i in range(1,len(predictions)+1):
            prediction = predictions[i-1]
            print prediction
            if prediction==1:
                print "suggesting", i
                return i
        print "-------- suggesting default"
        return 1
    else:
        print "---------- 1 suggesting default"
        return 1

def train(session_id, results, feedback):
    global prev_result
    global all_trees
    global all_data
    global all_y
    print prev_result
    results = prev_result
    newY = [0,0,0]
    newY[feedback-1] = 1
    newData = []
    print "asdjkahsdksjhdad"
    keys = range(1,len(results.keys())+1)
    print results
    for key in keys:
        num_reviews = results[key]["reviews"]
        rating = results[key]["rating"]
        row = [num_reviews,rating]
        newData.append(row)
    print keys
    if session_id in all_trees:
        data = all_data[session_id]
        y = all_y[session_id]
        newData = newData + data
        newY = newY + y
    print "----", newData, newY
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(newData, newY)
    all_trees[session_id] = clf
    all_y[session_id] = newY
    all_data[session_id] = newData

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
    global prev_result
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
    result = getResults(query)
    print request['session_id']
    print result
    if result:
        #template = []
        #for key, r in result.items():
        #    element = {}
        #    element['title'] = r['name']
        #    element['subtitle'] = ' '.join(r['address'])
        #    element['default_action'] = {'type': 'web_url', 'url': r['url']}
        #    template.append(element)
        #context['result'] = '' 
        for key, r in result.items():
            context['result'+str(key)] = str(key) + '. ' + r['name'] + ' situated at ' + ' '.join(result[1]['address'])
        #context['name'] = result[1]['name']
        #context['address'] = result[1]['address']
        #templatecontext['url'] = result[1]['url']
    context['original'] = result
    prev_result = result
    print prev_result, result, "----------------------------------"
    context['suggest'] = suggest(request['session_id'], result)
    return context

def train_agent(request):
    print request
    context = request['context']
    feedback = int(first_entity_value(request['entities'], 'feedback'))
    print feedback, "-----------------", context
    train(request['session_id'], '',feedback)

def send(request, response):
    send_message(PAT, request['session_id'], response['text'])

actions = {
    'send': send,
    'echo_entities': echo_entities,
    'train': train_agent
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
        wit_client.run_actions(message=message, session_id=sender, max_steps=10)
    except Exception as error:
        print "///////////////////////"
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
