"""
Meteostat JSON API Server

The code is licensed under the MIT license.
"""

import os
from configparser import ConfigParser
from flask import request, Response
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from urllib.parse import quote_plus

# Path of configuration file
config_path: str = os.path.expanduser('~') + os.sep + '.meteostat-server' + os.sep + 'config.ini'


def get_config() -> ConfigParser:
    """
    Get data from configuration file with environment variable overrides.

    Supported environment variables:
    - METEOSTAT_SERVER_NAME
    - METEOSTAT_SECRET_NAME, METEOSTAT_SECRET_VALUE, METEOSTAT_SECRET_DISABLE
    - METEOSTAT_DB_HOST, METEOSTAT_DB_PORT, METEOSTAT_DB_USER, METEOSTAT_DB_PASSWORD, METEOSTAT_DB_NAME
    - DATABASE_URL (overrides individual DB vars)
    """
    # Prepare configuration with optional defaults
    config = ConfigParser()

    # Provide default sections to avoid NoSectionError
    for section in ('server', 'secret', 'database'):
        if not config.has_section(section):
            config.add_section(section)

    # Read config file if present
    try:
        if os.path.exists(config_path):
            config.read(config_path)
    except Exception:
        # Ignore malformed config files to keep server running
        pass

    # Overlay environment variables
    if os.getenv('METEOSTAT_SERVER_NAME') is not None:
        config.set('server', 'name', os.getenv('METEOSTAT_SERVER_NAME', ''))

    if os.getenv('METEOSTAT_SECRET_NAME') is not None:
        config.set('secret', 'name', os.getenv('METEOSTAT_SECRET_NAME', ''))
    if os.getenv('METEOSTAT_SECRET_VALUE') is not None:
        config.set('secret', 'value', os.getenv('METEOSTAT_SECRET_VALUE', ''))
    if os.getenv('METEOSTAT_SECRET_DISABLE') is not None:
        config.set('secret', 'disable', os.getenv('METEOSTAT_SECRET_DISABLE', ''))

    # Database via individual vars unless DATABASE_URL is provided
    if os.getenv('DATABASE_URL'):
        config.set('database', 'url', os.getenv('DATABASE_URL', ''))
    else:
        for key, env in (
            ('host', 'METEOSTAT_DB_HOST'),
            ('port', 'METEOSTAT_DB_PORT'),
            ('user', 'METEOSTAT_DB_USER'),
            ('password', 'METEOSTAT_DB_PASSWORD'),
            ('name', 'METEOSTAT_DB_NAME'),
        ):
            if os.getenv(env) is not None:
                config.set('database', key, os.getenv(env, ''))

    return config


def _build_database_engine(config: ConfigParser) -> Engine:
    """
    Build a SQLAlchemy engine from config, supporting DATABASE_URL or individual MySQL settings.
    """
    url = ''
    if config.has_option('database', 'url'):
        url = config.get('database', 'url')

    if url:
        return create_engine(url)

    # Fall back to individual components
    user = config.get('database', 'user', fallback='')
    password = config.get('database', 'password', fallback='')
    host = config.get('database', 'host', fallback='localhost')
    port = config.get('database', 'port', fallback='3306')
    name = config.get('database', 'name', fallback='')

    # URL-encode password to be safe
    password_enc = quote_plus(password)
    conn_url = f"mysql+mysqlconnector://{user}:{password_enc}@{host}:{port}/{name}?charset=utf8"

    # Pre-ping helps avoid stale connections in some environments
    engine = create_engine(conn_url, pool_pre_ping=True)
    return engine


def db_query(query: str, payload: dict | None = None):
    """
    Query data from SQL database and return the SQLAlchemy CursorResult.
    """
    # Get configuration
    config = get_config()

    database = _build_database_engine(config)

    with database.connect() as con:
        # autocommit execution option is deprecated; SELECTs don't need it
        return con.execute(text(query), payload or {})


def get_parameters(parameters: list):
    """
    Get request parameters
    """

    args = {}

    for parameter in parameters:
        value = request.args.get(parameter[0])
        if parameter[1] == bool and (value == '0' or value == 'false'):
            value = False
        args[parameter[0]] = parameter[1](value) if value != None else parameter[2]

    return args


def send_response(output: str, cache_time: int = 0) -> Response:
    """
    Send a response
    """

    # Create response in JSON format
    resp = Response(output, mimetype='application/json')

    # Set cache header
    if cache_time == 0:
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
    else:
        resp.headers['Cache-Control'] = f'public, must-revalidate, max-age={cache_time}'

    # Return
    return resp
