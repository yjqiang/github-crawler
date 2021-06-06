import time

from request_websession import WebSession
import utils

# To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
# https://stackoverflow.com/questions/61810553/how-to-get-more-than-1000-search-results-with-api-github

# 配置文件（私有）
conf = utils.toml_load('conf/conf.toml')
api_token = conf['user']['api_token']

headers = {
    'Authorization': 'token ' + api_token,
    'Accept': 'application/vnd.github.v3+json',
}

session = WebSession()

url = 'https://api.github.com/search/code'
params = {
    'q': 'class nn.module in:file extension:py',
    'per_page': 100,
    'page': None
}


results = {'results': []}
for page in range(1, 11):
    params['page'] = page
    response = session.request_json('GET', url=url, params=params, headers=headers)
    items = response['items']
    for item in items:
        repository_info = item['repository']
        owner_info = repository_info['owner']
        results['results'].append({
            'repository_url': repository_info['html_url'],  # 仓库地址
            'code_url': item['html_url'],  # 该仓库那个文件查出来了目标片段
            'owner': {
                'name': owner_info['login'],  # 用户名
                'id': owner_info['id'],  # 用户 id
            }
        })
    time.sleep(2)
utils.save_json('clawer/data.json', results)
