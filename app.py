"""
Meteostat JSON API Server

The code is licensed under the MIT license.
"""

import os
from server import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)
