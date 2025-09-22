"""
Official Meteostat JSON API Server

The code is licensed under the MIT license.
"""

__appname__ = 'server'
__version__ = '0.0.16'

import warnings
from flask import Flask, request, abort, jsonify
from .utils import get_config

# Ignore warnings
warnings.filterwarnings('ignore')

# Create Flask app instance
app = Flask(__name__)

# Get configuration
config = get_config()

# Health endpoint (no auth)
@app.route('/health', methods=['GET'])
def health():
    return jsonify(status='ok'), 200

# Check secret header
@app.before_request
def secret():
    # Skip auth for health and root
    if request.path in ('/', '/health'):
        return None

    # Allow disabling via config or env
    disable = False
    try:
        disable = config.getboolean('secret', 'disable', fallback=False)
    except Exception:
        disable = False

    if disable:
        return None

    # Get header name & value with safe fallbacks
    name = None
    value = None
    try:
        name = config.get('secret', 'name', fallback=None)
        value = config.get('secret', 'value', fallback=None)
    except Exception:
        name = None
        value = None

    # If not configured, don't enforce
    if not name or not value:
        return None

    # Enforce header
    if request.headers.get(name) != value:
        abort(401)


@app.after_request
def poweredby(resp):
    server_name = 'meteostat-server'
    try:
        server_name = config.get('server', 'name', fallback=server_name)
    except Exception:
        pass
    resp.headers['X-Meteostat-Server'] = server_name
    return resp

# Root endpoint for quick check
@app.route('/')
def index():
    return jsonify(app=__appname__, version=__version__), 200

# Import API endpoints
from .endpoints.stations.meta import *
from .endpoints.stations.nearby import *
from .endpoints.stations.hourly import *
from .endpoints.stations.daily import *
from .endpoints.stations.monthly import *
from .endpoints.stations.normals import *
from .endpoints.point.hourly import *
from .endpoints.point.daily import *
from .endpoints.point.monthly import *
from .endpoints.point.normals import *
