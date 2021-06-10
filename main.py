import asyncio
import os
import re
from typing import Optional

from aiohttp_websession import WebSession
import utils
from crawler.handlers import Handlers, SearchCodeHandler, ListStargazersHandler

# To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
# https://stackoverflow.com/questions/61810553/how-to-get-more-than-1000-search-results-with-api-github

# 配置文件（私有）
conf = utils.toml_load('conf/conf.toml')
API_TOKENS = [item['api_token'] for item in conf['users']]


class Crawler:
    def __init__(self, list_results: Optional[list[str]]):
        self.session = WebSession()
        self.list_results = list_results

    async def search_code(self, query: str) -> list[dict]:
        """
        搜索代码
        :return:
        """
        handlers = Handlers(SearchCodeHandler, api_tokens=API_TOKENS, query=query)
        results = []
        for page in range(1, 11):
            handler = handlers.choice()
            handler.params['page'] = page

            response = await self.session.request_json('GET', url=handler.url, params=handler.params, headers=handler.headers)
            await asyncio.sleep(1)

            if not response:
                break
            items = response['items']
            if not items:
                break
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

        return results

    async def list_repo_stars(self, username: str, repo_name: str) -> list[dict]:
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
            response = await self.session.request_json('GET', url=handler.url, params=handler.params, headers=handler.headers)
            await asyncio.sleep(1)

            if not response:
                break
            for item in response:
                results.append({
                    'name': item['login'],
                })

        return results

    async def handler_one_round(self, username: str) -> set[str]:
        """
        :param username:
        :return:
        """
        # 获取新的符合规定的代码片段
        cur_result = await self.search_code(f'user:{username} class nn.module in:file extension:py')  # 搜索某用户下面所有仓库中，含有某关键词的仓库代码
        set_files = set(item['repository_url'] for item in cur_result)

        self.list_results += list(set(item['repository_url'] for item in cur_result))

        repository_url_parse_pattern = re.compile(r'^https://github\.com/([^/]+)/(.+)$')
        # 通过仓库的 followers 查找有机器学习仓库的用户
        set_users = set()
        for repository_url in set_files:  # type: str
            match_result = repository_url_parse_pattern.fullmatch(repository_url)
            cur_result = await self.list_repo_stars(match_result.group(1), match_result.group(2))
            set_users |= set(item['name'] for item in cur_result)
            print(f'DONE list_repo_stars user {match_result.group(1)}(cur_len: {len(set_users)})')

        return set_users


async def main():
    crawler = Crawler(None)
    todo_jobs_queue = asyncio.Queue()

    if not os.path.isfile('crawler/data.json'):  # 是个存在的文件；如果存在说明已经有了初始化的数据了
        # 初始化（可以看作是第 0 层的递归深度结果）
        if not os.path.isfile('crawler/data0.json'):  # 是个存在的文件
            results = await crawler.search_code('class nn.module in:file extension:py')  # 搜索 Github 所有仓库中，含有某关键词的仓库代码
            utils.save_json('crawler/data0.json', {'results': results})
        else:
            results = utils.open_json('crawler/data0.json')['results']

        list_todo_jobs = list(set(item['owner']['name'] for item in results))  # 还未处理的“新”用户
        set_users = set(list_todo_jobs)  # 已经完成 handler_one_round 的 user 集合 + todo_jobs（用于任务执行去重）
        list_results = []  # 截止目前为止搜到的仓库

        utils.save_json('crawler/data.json', {
            'list_todo_jobs': list_todo_jobs,
            'set_users': list(set_users),
            'list_results': list_results,
        })
    else:
        cur_result = utils.open_json('crawler/data.json')
        list_todo_jobs = cur_result['list_todo_jobs']  # 还未处理的“新”用户
        set_users = set(cur_result['set_users'])  # 已经完成 handler_one_round 的 user 集合 + todo_jobs（用于任务执行去重）
        list_results = cur_result['list_results']  # 截止目前为止搜到的仓库

    for todo_job in list_todo_jobs:
        await todo_jobs_queue.put(todo_job)
    crawler.list_results = list_results

    while len(crawler.list_results) < 10000:
        print(f'PREPARING and cur_result: {len(crawler.list_results)}')
        # 通过仓库的 followers 查找有机器学习仓库的用户

        cur_max_number_of_jobs = 3
        cur_todo_jobs = []
        while (not todo_jobs_queue.empty()) and cur_max_number_of_jobs > 0:
            cur_todo_jobs.append(await todo_jobs_queue.get())
            cur_max_number_of_jobs -= 1

        if not cur_todo_jobs:  # 没有要干的活儿了
            break

        cur_results = await asyncio.gather(
            *[crawler.handler_one_round(todo_job) for todo_job in cur_todo_jobs]
        )

        for cur_result in cur_results:
            cur_result -= set_users  # 重复的用户不再重复处理！！
            for todo_job in cur_result:
                await todo_jobs_queue.put(todo_job)
            set_users |= cur_result  # 用于任务执行去重

        with open('test.txt', 'w+', encoding='utf8') as f:
            for item in crawler.list_results:
                f.write(f'{item}\n')

    list_todo_jobs = []
    while not todo_jobs_queue.empty():
        list_todo_jobs.append(await todo_jobs_queue.get())
    utils.save_json(f'crawler/data.json', {
        'list_todo_jobs': list_todo_jobs,
        'set_users': list(set_users),
        'list_results': crawler.list_results,
    })

    await crawler.session.session.close()


if __name__ == '__main__':
    asyncio.run(main())
