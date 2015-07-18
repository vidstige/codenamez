import os
from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory
import pymongo

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

def _prefixes(s):
	return s['prefixes'] or []

def _suffixes(s):
	return s['suffixes'] or []

def create_name(db, serie):
	series_collection = db.series

	versions_collection_name = "{}-versions".format(serie)
	versions_collection = db[versions_collection_name]

	s = db.series.find_one({'serie': serie})
	if s is None:
		raise Exception('No such serie: "{}"'.format(serie))

	for prefix in _prefixes(s):
		for suffix in _suffixes(s):
			name = "{}-{}".format(prefix, suffix)
    		document = versions_collection.find_one({'name': name})
    		if document is None:
    			return name

	raise Exception("{} exhausted".format(serie))

@app.route('/get-codename/<serie>/<version>')
def get_codename(serie, version):
	conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
	db = conn[os.environ['OPENSHIFT_APP_NAME']]

	versions_collection_name = "{}-versions".format(serie)
	versions_collection = db[versions_collection_name]

	document = versions_collection.find_one({'version': version})
	if (document is not None):
		return document['name']

	name = create_name(db, serie)
	versions_collection.insert_one({'version': version, 'name': name})

	return name

@app.route('/lookup-codename/<serie>/<name>')
def lookup_codename(serie, name):
	conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
	db = conn[os.environ['OPENSHIFT_APP_NAME']]

	versions_collection_name = "{}-versions".format(serie)
	versions_collection = db[versions_collection_name]

	document = versions_collection.find_one({'name': name})
	if (document is None):
		return "Code name '{}' not found".format(name), 404
	
	return document['version']

@app.route('/add-serie/', methods=['POST'])
def add_serie():
	conn = pymongo.MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])
	db = conn[os.environ['OPENSHIFT_APP_NAME']]

	db.series.insert({
			'serie': request.form['serie'],
			'prefixes': request.form['prefixes'].split(),
			'suffixes': request.form['suffixes'].split()
		})

	return "Serie added. Don't refresh page."

@app.route("/test")
def test():
    return "<strong>It's Alive!</strong>"

if __name__ == '__main__':
    app.run()
