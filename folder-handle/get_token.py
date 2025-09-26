from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# 使用您的客户端信息
client_config = {
    "installed": {
        "client_id": "575740363190-1ieco6aboa5255vvla1gqqdm76osep83.apps.googleusercontent.com",
        "client_secret": "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",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

flow = Flow.from_client_config(
    client_config,
    scopes=['https://www.googleapis.com/auth/drive'],
    redirect_uri='http://localhost'
)

auth_url, _ = flow.authorization_url(prompt='consent')
print('请访问以下URL进行授权:')
print(auth_url)

# 获取授权码
code = input('请输入重定向后的代码: ')
flow.fetch_token(code=code)

creds = flow.credentials
print('Access Token:', creds.token)
print('Refresh Token:', creds.refresh_token)