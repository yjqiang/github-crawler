import json

from request_websession import WebSession

url = 'https://api.github.com/graphql'
query = '''
repository(owner:"aio-libs", name:"aiohttp") {
    issues(last:20, states:CLOSED) {
        edges {
            node {
                title
                url
                labels(first:5) {
                    edges {
                        node {
                            name
                            pullRequests{totalCount}
                        }
                    }
                }
            }
            cursor
        }
    }
}
'''

api_token = "xxxxxxx"
headers = {
    "Content-Type": "application/json",
    'Authorization': f'token {api_token}'
}

session = WebSession()
response = session.request_json('POST', url=url, json={'query': f'{{{query}}}'}, headers=headers)
print(json.dumps(response, indent=4))
