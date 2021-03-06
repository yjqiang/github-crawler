"""
下载仓库
"""
import asyncio
import re

from aiohttp_websession import WebSession
import utils
from crawler.handlers import Users, DownloadRepoZipHandler0, DownloadRepoZipHandler1

# To satisfy that need, the GitHub Search API provides up to 1,000 results for each search.
# https://stackoverflow.com/questions/61810553/how-to-get-more-than-1000-search-results-with-api-github

# 配置文件（私有）
conf = utils.toml_load('conf/conf.toml')
api_tokens = [item['api_token'] for item in conf['users']]
users = Users(api_tokens)


class Crawler:
    def __init__(self):
        self.session = WebSession()
        self.number_success = 0
        self.list_results = []

    async def handler_one_round(self, repository_url: str) -> None:
        """
        :param repository_url:
        :return:
        """
        repository_url_parse_pattern = re.compile(r'^https://github\.com/([^/]+)/(.+)$')
        match_result = repository_url_parse_pattern.fullmatch(repository_url)

        username = match_result.group(1)
        repo_name = match_result.group(2)

        handler = DownloadRepoZipHandler0(username=username, repo_name=repo_name)  # master branch
        users.equip_1_handler(handler)  # 代入一个用户
        data = await self.session.request_stream('GET', url=handler.url, params=handler.params, headers=handler.headers)
        if data is None:
            handler = DownloadRepoZipHandler1(username=username, repo_name=repo_name)  # main branch
            users.equip_1_handler(handler)  # 代入一个用户
            data = await self.session.request_stream('GET', url=handler.url, params=handler.params, headers=handler.headers)

        if data is not None:
            with open(f'download_repos/result/{username}-{repo_name}.zip', 'wb') as f:
                f.write(data)
            print(f'DONE {username}-{repo_name}.zip')
            self.number_success += 1
            self.list_results.append([username, repo_name, f'{username}-{repo_name}.zip'])


async def main():
    crawler = Crawler()
    todo_jobs_queue = asyncio.Queue()

    cur_result = utils.open_json('crawler/result/data.json')
    list_todo_jobs = cur_result['list_results']  # 截止目前为止搜到的仓库

    for todo_job in list_todo_jobs:
        await todo_jobs_queue.put(todo_job)

    while not todo_jobs_queue.empty():
        print(f'PREPARING and remaining: {todo_jobs_queue.qsize()} and cur_result: {crawler.number_success}/{len(list_todo_jobs)}')

        cur_max_number_of_jobs = 2
        cur_todo_jobs = []
        while (not todo_jobs_queue.empty()) and cur_max_number_of_jobs > 0:
            cur_todo_jobs.append(await todo_jobs_queue.get())
            cur_max_number_of_jobs -= 1

        if not cur_todo_jobs:  # 没有要干的活儿了
            break

        await asyncio.gather(
            *[crawler.handler_one_round(todo_job) for todo_job in cur_todo_jobs]
        )

    await crawler.session.session.close()
    utils.save_json(f'download_repos/result/data.json', {
        'list_results': crawler.list_results,
    })


if __name__ == '__main__':
    asyncio.run(main())
