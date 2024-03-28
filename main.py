from fastapi import FastAPI, HTTPException
from cachetools import TTLCache

import requests

app = FastAPI()

# Cache with a TTL (time-to-live) of 300 seconds (5 minutes)
cache = TTLCache(maxsize=100, ttl=300)

@app.post("/proxy")
async def proxy_get(url: str, headers: dict = None):
    return proxy_request("GET", url, headers)

def proxy_request(method: str, url: str, headers: dict = None, data: dict = None):
    if url in cache:
        # If the URL is in the cache, return the cached response
        return cache[url]
    else:
        # If the URL is not in the cache, make a request to the URL
        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for bad status codes
            result = response.json() if response.headers.get('content-type') == 'application/json' else response.content
            cache[url] = result  # Cache the response
            return result
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
