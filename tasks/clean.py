"""
Meteostat JSON API Server

The code is licensed under the MIT license.
"""

import os
from meteostat import Hourly, Daily, Monthly, Normals

# Configurable cache directory (default inside container/app)
cache_dir = os.environ.get('METEOSTAT_CACHE_DIR', '/app/.meteostat/cache')
os.makedirs(cache_dir, exist_ok=True)
Hourly.cache_dir = cache_dir
Daily.cache_dir = cache_dir
Monthly.cache_dir = cache_dir
Normals.cache_dir = cache_dir

# Max. cache time
max_cache_time = 60 * 60 * 24 * 30

# Clear hourly cache
Hourly.clear_cache(max_cache_time)

# Clear daily cache
Daily.clear_cache(max_cache_time)

# Clear monthly cache
Monthly.clear_cache(max_cache_time)

# Clear normals cache
Normals.clear_cache(max_cache_time)
