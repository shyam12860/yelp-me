# Entities looking for:
# Cost
# Datetime
# Cuisine
# Rating
# Location

from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
import json

def getResults(entityDict):
	auth = Oauth1Authenticator(
	    consumer_key="GnqVNHo3kMwUkjHtcKTAiQ",
	    consumer_secret="pAAALBgFrBrnfV4wUm4Q-gnRQK0",
	    token="X1adQAiL7lfMu4x0DFLypmDXMJTeR45_",
	    token_secret="6ol3E34GGqZm-rBF-M8U9HsSt7M"
	)

	client = Client(auth)

	LOCATION = entityDict['location']
	CUISINE = entityDict['cuisine']
	COST = entityDict['cost']
	RATING = entityDict['rating']
	DATETIME = entityDict['datetime']

	if(DATETIME):
		HOUR = DATETIME.split('T')[1][0:2]
	else:
		HOUR=""

	CUISINE = CUISINE if CUISINE else ""
	COST = COST if COST else ""
	RATING = float(RATING) if RATING else 0.0

	params = {
	    'term': COST + ' ' + CUISINE + ' ' + 'restaurants' + ' which remain open at '+ HOUR,
	    'sort': "0",
	    'limit': '3'
	}

	if(LOCATION==None):
		return {}

	response = client.search(LOCATION, **params)
	d = {}
	count = 1
	for i in range(0,len(response.businesses)):
		if(response.businesses[i].rating>=RATING):
			d[count] = {}
			d[count]["name"] = response.businesses[i].name
			d[count]["url"] = response.businesses[i].url
			d[count]["address"] = response.businesses[i].location.address
			d[count]["rating"] = response.businesses[i].rating
			d[count]["reviews"] = response.businesses[i].review_count
			count+=1
	
	return d
