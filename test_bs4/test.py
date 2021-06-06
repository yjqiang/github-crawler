from bs4 import BeautifulSoup

from request_websession import WebSession

request_data = {
    "url": "https://github.com/search?p=3&q=nn.module+in%3Afile+extension%3Apy&type=Code&_pjax=%23js-pjax-container",
    "method": "GET",
    "data": None,
    "headers": {
        "authority": "github.com",
        "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
        "dnt": "1",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "accept": "text/html",
        "x-requested-with": "XMLHttpRequest",
        "x-pjax": "true",
        "x-pjax-container": "#js-pjax-container",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://github.com/search?p=3&q=nn.module+in%3Afile+extension%3Apy&type=Code",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": ""
    }
}


session = WebSession()


response = session.request_text(request_data['method'], request_data['url'], headers=request_data['headers'])
soups = BeautifulSoup(response, 'lxml')
