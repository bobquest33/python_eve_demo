#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instantiates the Python Eve REST API Server.

Instantiates the Python Eve REST API Server for both local
and cloud (IBM Bluemix) execution.  Provides a default catch-all
routing to provide API consumers with intentional responses
for all routes.  Provides a redis cloud caching instance for
session management where desired.
"""

import os
import json
import re

__author__ = "Priyabrata Dash"
__copyright__ = "IBM Copyright 2017"
__credits__ = ["PRUDENTIAL RETIREMENT"]
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Priyabrata Dash"
__email__ = "pridash4@in.ibm.com"
__status__ = "Prototype"

DEBUG = True

SWAGGER_INFO={
    'title': 'Blockchain Loans Processing Demo',
    'version': '0.01 beta',
    'description': 'This demo is to show how to track Loans Processing using IBM Blockchain',
    'termsOfService': '',
    'contact': {
        'name': 'PRUDENTIAL RETIREMENT',
        'url': 'https://git.ng.bluemix.net/IT2017_TEAM17041417233100699/it2017_team17041417233100699'
    },
    'license': {
        'name': 'BSD',
        'url': 'https://git.ng.bluemix.net/IT2017_TEAM17041417233100699/it2017_team17041417233100699',
    }
}

# Initialize Objects
# capture current working directory
PWD = os.getenv("PWD")
# set default host and ports (change 5000 to avoid airplay collision)
APP_HOST = '0.0.0.0'
APP_PORT = os.getenv('PORT', '5005')
VCAP_CONFIG = os.getenv('VCAP_SERVICES')
VCAP_APPLICATION = os.getenv('VCAP_APPLICATION')
APP_URI = 'http://0.0.0.0:5005'
SQLALCHEMY_DATABASE_URI='postgresql://pridash4@localhost:5432/postgres'

# Detect if we are deployed within Bluemix or not and act accordingly
if VCAP_CONFIG:
    # We're hosted on Bluemix! Use the MongoLabs sandbox as our backend.
    # Read the VCAP_APPLICATION environment variable to get its route
    decoded_application = json.loads(VCAP_APPLICATION)
    APP_URI = 'http://' + decoded_application['application_uris'][0]
    SERVER_NAME = decoded_application['application_uris'][0]
    # Read the VCAP_SERVICES environment variable
    decoded_config = json.loads(VCAP_CONFIG)
    # Loop through the service instances to capture connection info
    #for key, value in decoded_config.iteritems():
    for key, value in decoded_config.items():
        # Looking for an instance of a Mongo Bluemix Service
        print(key,":",value)
        if key.startswith('postgresql') or key.startswith('elephantsql'):
            postgres_creds = decoded_config[key][0]['credentials']
            seq = (r'^postgresql\:\/\/(?P<username>[\W\w]+):(?P<password>[\W\w]+)'
                   '@'
                   '(?P<host>[\.\w]+):(?P<port>\d+)/(?P<database>[\W\w]+).*?$')
            regex = re.compile(seq)
            match = regex.search(postgres_creds['uri'])
            # Deconstruct PostgresURL connection information
            parseURI = match.groupdict()
            POSTGRES_HOST = parseURI['host']
            POSTGRES_PORT = int(parseURI['port'])
            POSTGRES_USERNAME = parseURI['username']
            POSTGRES_PASSWORD = parseURI['password']
            POSTGRES_DBNAME = parseURI['database']
            SQLALCHEMY_DATABASE_URI=postgres_creds
            continue

# Enable URL_PREFIX.  Used in conjunction with API_VERSION to build
# API Endpoints of the form <base_route>/<url_prefix>/<api_version>/
URL_PREFIX = 'api'

# Enable API Versioning.  This will force API Calls to follow a form of
# <base_route>/<api_version>/<resource_title>/...
API_VERSION = 'v1'

# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

# Accept-Language request headers
LANGUAGE_DEFAULT = 'en'
LANGUAGES = {
    'en': 'English',
    'es': 'Espanol',
    'fr': 'French',
    'pt': 'Portuguese',
    'ar': 'Arabic'
}

# We enable Cross Origin Resource Sharing (CORS) to facilitate swagger.io
X_DOMAINS = '*'
X_HEADERS = ['Origin', 'X-Requested-With', 'Content-Type', 'Accept']

# Our API will expose the following resources (MongoDB collections):
# 'mac', ...
# In order to allow for proper data validation, we define behaviour
# and structure.


SWAGGER_URL = '/api-docs-ui'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/api-docs'  # Our API url (can of course be a local resource)
