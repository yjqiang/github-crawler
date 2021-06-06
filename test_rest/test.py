import json

from request_websession import WebSession

# To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
# https://stackoverflow.com/questions/61810553/how-to-get-more-than-1000-search-results-with-api-github

api_token = "xxxxxxx"
headers = {
    'Authorization': 'token ' + api_token,
    'Accept': 'application/vnd.github.v3+json',
}

session = WebSession()


response = session.request_json('GET', 'https://api.github.com/user', headers=headers)
print(json.dumps(response, indent=4))

url = 'https://api.github.com/search/code'
params = {
    'q': 'nn.module in:file extension:py',
    'page': 50
}
response = session.request_json('GET', url=url, params=params, headers=headers)
print(json.dumps(response, indent=4))


