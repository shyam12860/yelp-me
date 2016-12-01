from yelpScript import getResults

json = {'cost': None, 'datetime': None, 'cuisine': None, 'rating':None, 'location': 'Atlanta'}
d = getResults(json)
print d