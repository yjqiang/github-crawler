import random


class ApiHandler:
    def __init__(self, api_token: str):
        self.url = 'https://api.github.com'
        self.method = 'GET'
        self.headers = {
            'Authorization': 'token ' + api_token,
            'Accept': 'application/vnd.github.v3+json',
        }
        self.params = {}


class SearchCodeHandler(ApiHandler):
    def __init__(self, api_token: str, query: str):
        super().__init__(api_token)
        self.url = 'https://api.github.com/search/code'
        self.params = {
            'q': query,
            'per_page': 100,
            'page': None
        }


class ListReposHandler(ApiHandler):
    def __init__(self, api_token: str, username: str):
        super().__init__(api_token)
        self.url = f'https://api.github.com/users/{username}/repos'
        self.params = {
            'per_page': 100,
            'page': None
        }


class ListStargazersHandler(ApiHandler):  # 查看某仓库的关注者
    def __init__(self, api_token: str, username: str, repo_name: str):
        super().__init__(api_token)
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/stargazers'
        self.params = {
            'per_page': 100,
            'page': None
        }


class DownloadRepoZipHandler0(ApiHandler):  # 下载 zip
    def __init__(self, api_token: str, username: str, repo_name: str):
        super().__init__(api_token)
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/zipball/master'
        self.headers = {
            'Authorization': 'token ' + api_token,
        }


class DownloadRepoZipHandler1(ApiHandler):  # 下载 zip
    def __init__(self, api_token: str, username: str, repo_name: str):
        super().__init__(api_token)
        self.url = f'https://api.github.com/repos/{username}/{repo_name}/zipball/main'
        self.headers = {
            'Authorization': 'token ' + api_token,
        }


class Handlers:
    def __init__(self, handler, api_tokens: list[str], *args, **kwargs):
        self.handlers = [handler(api_token, *args, **kwargs) for api_token in api_tokens]

    def choice(self) -> ApiHandler:
        return random.choice(self.handlers)
