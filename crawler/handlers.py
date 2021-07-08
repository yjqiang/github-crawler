import random


class ApiHandler:
    def __init__(self):
        self.url = 'https://api.github.com'
        self.method = 'GET'
        self.headers = {
            'Authorization': None,
            'Accept': 'application/vnd.github.v3+json',
        }
        self.params = {}

    def equip(self, api_token: str) -> None:
        self.headers['Authorization'] = 'token ' + api_token


class SearchCodeHandler(ApiHandler):
    def __init__(self, query: str):
        super().__init__()
        self.url = 'https://api.github.com/search/code'
        self.params = {
            'q': query,
            'per_page': 100,
            'page': None
        }


class ListReposHandler(ApiHandler):
    def __init__(self, username: str):
        super().__init__()
        self.url = f'https://api.github.com/users/{username}/repos'
        self.params = {
            'per_page': 100,
            'page': None
        }


class ListStargazersHandler(ApiHandler):  # 查看某仓库的关注者
    def __init__(self, username: str, repo_name: str):
        super().__init__()
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/stargazers'
        self.params = {
            'per_page': 100,
            'page': None
        }


class DownloadRepoZipHandler0(ApiHandler):  # 下载 zip
    def __init__(self, username: str, repo_name: str):
        super().__init__()
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/zipball/master'
        self.headers = {
            'Authorization': None,
        }


class DownloadRepoZipHandler1(ApiHandler):  # 下载 zip
    def __init__(self, username: str, repo_name: str):
        super().__init__()
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/zipball/main'
        self.headers = {
            'Authorization': None,
        }


class Users:
    def __init__(self, api_tokens: list[str]):
        self.users = api_tokens

    def equip_1_handler(self, api_handler: ApiHandler) -> None:
        """
        随机挑选一个用户，装配到 handler 里面
        :param api_handler:
        :return:
        """
        api_handler.equip(random.choice(self.users))
