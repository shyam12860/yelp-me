from yelpScript import getResults

json = {'cost': u'cheap', 'datetime': u'2016-12-01T08:00:00.000-08:00', 'cuisine': u'american', 'rating': u'2.0', 'location': u'Atlanta'}
d = getResults(json)
print d