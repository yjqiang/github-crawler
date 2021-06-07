import time
import os
import re

from request_websession import WebSession
import utils
from crawler.handlers import Handlers, SearchCodeHandler, ListStargazersHandler

# To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
# https://stackoverflow.com/questions/61810553/how-to-get-more-than-1000-search-results-with-api-github

# 配置文件（私有）
conf = utils.toml_load('conf/conf.toml')
API_TOKENS = [item['api_token'] for item in conf['users']]

SESSION = WebSession()


def search_code(query: str) -> list[dict]:
    """
    搜索代码
    :return:
    """
    handlers = Handlers(SearchCodeHandler, api_tokens=API_TOKENS, query=query)
    results = []
    for page in range(1, 11):
        handler = handlers.choice()
        handler.params['page'] = page
        response = SESSION.request_json('GET', url=handler.url, params=handler.params, headers=handler.headers)
        items = response['items']
        for item in items:
            repository_info = item['repository']
            owner_info = repository_info['owner']
            results.append({
                'repository_url': repository_info['html_url'],  # 仓库地址
                'code_url': item['html_url'],  # 该仓库那个文件查出来了目标片段
                'owner': {
                    'name': owner_info['login'],  # 用户名
                    'id': owner_info['id'],  # 用户 id
                }
            })

        time.sleep(1)
        if not items:
            break
    return results


def list_repo_stars(username: str, repo_name: str) -> list[dict]:
    """
    搜索仓库代码的 star 人
    :param repo_name:
    :param username:
    :return:
    """
    handlers = Handlers(ListStargazersHandler, api_tokens=API_TOKENS, username=username, repo_name=repo_name)
    results = []
    for page in range(1, 11):
        handler = handlers.choice()
        handler.params['page'] = page
        response = SESSION.request_json('GET', url=handler.url, params=handler.params, headers=handler.headers)
        time.sleep(0.5)
        if not response:
            break
        for item in response:
            results.append({
                'name': item['login'],
            })

    return results


def main():
    if not os.path.isfile('crawler/data.json'):  # 是个存在的文件；如果存在说明已经有了初始化的数据了
        # 初始化（可以看作是第 0 层的递归深度结果）

        if not os.path.isfile('crawler/data0.json'):  # 是个存在的文件
            results0 = search_code('class nn.module in:file extension:py')  # 搜索 Github 所有仓库中，含有某关键词的仓库代码
            utils.save_json('crawler/data0.json', {'results': results0})
        else:
            results0 = utils.open_json('crawler/data0.json')['results']
        set_users = set(item['owner']['name'] for item in results0)  # 用户去重

        if not os.path.isfile('crawler/data1.json'):  # 是个存在的文件
            results1 = []
            for username in set_users:
                results1 += search_code(f'user:{username} class nn.module in:file extension:py')  # 搜索某用户下面所有仓库中，含有某关键词的仓库代码
                print(f'DONE user {username}(cur_len: {len(results1)})')
            utils.save_json('crawler/data1.json', {'results': results1})
        else:
            results1 = utils.open_json('crawler/data1.json')['results']
        set_files = set(item['repository_url'] for item in results1)

        list_set_files = list(set_files)
        utils.save_json('crawler/data.json', {
            'set_users': list(set_users),  # 已经完成搜索该用户下面所有含关键词的仓库的 users 集合
            'set_files': list_set_files,  # 截止目前为止搜到的仓库（包括 new_set_files）
            'new_set_files': list_set_files  # 刚刚获取到的代码片段（还未查到 stargazers 以及后续操作）
        })
        new_set_files = set_files  # 新加入的代码片段
    else:
        cur_result = utils.open_json('crawler/data.json')
        set_users = set(cur_result['set_users'])  # 已经完成搜索该用户下面所有含关键词的仓库的 users 集合
        set_files = set(cur_result['set_files'])  # 截止目前为止搜到的仓库（包括 new_set_files）
        new_set_files = set(cur_result['new_set_files'])  # 刚刚获取到的代码片段（还未查到 stargazers 以及后续操作）

    repository_url_parse_pattern = re.compile(r'^https://github\.com/([^/]+)/(.+)$')

    max_depth = 1
    for cur_depth in range(1, max_depth + 1):
        print(f'PREPARING {max_depth=}')
        # 通过仓库的 followers 查找有机器学习仓库的用户
        new_set_users = set()
        for repository_url in new_set_files:  # item === repository_url
            match_result = repository_url_parse_pattern.fullmatch(repository_url)
            cur_result = list_repo_stars(match_result.group(1), match_result.group(2))
            new_set_users |= set(item['name'] for item in cur_result)
            print(f'DONE user {match_result.group(1)}(cur_len: {len(new_set_users)})')
        new_set_users -= set_users  # 已经被搜索过的用户不再重复搜索

        # 获取新的符合规定的代码片段
        new_set_files = set()
        for username in new_set_users:
            cur_result = search_code(f'user:{username} class nn.module in:file extension:py')  # 搜索某用户下面所有仓库中，含有某关键词的仓库代码
            new_set_files |= set(item['repository_url'] for item in cur_result)
            print(f'DONE user {username}(cur_len: {len(new_set_files)})')
        new_set_files -= set_files

        # 更新 set_files 和 set_users
        set_files += new_set_files
        set_users += new_set_users

        utils.save_json(f'crawler/data.json', {
            'set_users': list(set_users),  # 已经完成搜索该用户下面所有含关键词的仓库的 users 集合
            'set_files': list(set_files),  # 已经完成的（包含刚刚获取到的）
            'new_set_files': list(new_set_files)  # 刚刚获取到的代码片段（还未查到 stargazers 以及后续操作）
        })


if __name__ == '__main__':
    main()
