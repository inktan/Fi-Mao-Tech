import datetime
import jwt
import base64
import json

def analyze_cookie_expiry(cookie_header):
    """分析Cookie中的时间限制"""
    print("=== Cookie时间限制分析 ===\n")
    
    # 解析Cookie字符串
    cookies = {}
    for cookie in cookie_header.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key] = value
    
    # 1. 分析CloudFront-Policy
    if 'CloudFront-Policy' in cookies:
        policy = cookies['CloudFront-Policy']
        try:
            # Base64解码
            decoded_policy = base64.b64decode(policy + '==').decode('utf-8')
            policy_data = json.loads(decoded_policy)
            expiry_timestamp = policy_data['Statement'][0]['Condition']['DateLessThan']['AWS:EpochTime']
            expiry_time = datetime.datetime.fromtimestamp(expiry_timestamp, datetime.timezone.utc)
            print(f"1. CloudFront-Policy 过期时间: {expiry_time} (UTC)")
        except Exception as e:
            print(f"1. CloudFront-Policy 解析失败: {e}")
    
    # 2. 分析_strava_CloudFront-Expires
    if '_strava_CloudFront-Expires' in cookies:
        expiry_ms = int(cookies['_strava_CloudFront-Expires'])
        expiry_time = datetime.datetime.fromtimestamp(expiry_ms/1000, datetime.timezone.utc)
        print(f"2. _strava_CloudFront-Expires: {expiry_time} (UTC)")
    
    # 3. 分析_strava_idcf (JWT Token)
    if '_strava_idcf' in cookies:
        token = cookies['_strava_idcf']
        try:
            # 解码JWT payload（不验证签名）
            payload = jwt.decode(token, options={"verify_signature": False})
            if 'exp' in payload:
                expiry_time = datetime.datetime.fromtimestamp(payload['exp'], datetime.timezone.utc)
                print(f"3. _strava_idcf JWT过期时间: {expiry_time} (UTC)")
            if 'athleteId' in payload:
                print(f"   关联运动员ID: {payload['athleteId']}")
        except Exception as e:
            print(f"3. JWT解析失败: {e}")
    
    # 计算剩余时间
    now = datetime.datetime.now(datetime.timezone.utc)
    time_remaining = expiry_time - now
    print(f"\n剩余有效时间: {time_remaining}")
    
    return expiry_time

# 使用示例
cookie_string = "sp=8d609c8e-2bb0-4dd3-812b-565b0fde7d36; _strava4_session=ev98m1l7d2eocv1i9pc8q72dh99rvbvo; CloudFront-Key-Pair-Id=K3VK9UFQYD04PI; CloudFront-Policy=eyJTdGF0ZW1lbnQiOiBbeyJSZXNvdXJjZSI6Imh0dHBzOi8vKmNvbnRlbnQtKi5zdHJhdmEuY29tL2lkZW50aWZpZWQvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc2MTIwMzU5Mn19fV19; CloudFront-Signature=cZuzM5e~BWZ4JhGa2chpJV-d~UqU1JHQ~EWNZIJr5ds19QjrIaHzjCXnd6PdNq2riHgTKHTF8-pgGx6885rny-6B0htECFj1~L970p~aF~DQR3AG~e0LdMiqx8OGoeCkgfbJpJi1ythZNpFvGv1DpDH3b8BAtWshjusfua0k71UA2ull9CGkiPJ9SfQHpVMTduFr9MVCK7rDGgqQU-nLxR9bbmMcZRFQtpVOzm9KzIzbtEjP-zITS4HDiMQt-APMn1qktjyL0YlDZJOcPYDKD-0JznJHCkiXE7Ka0avHgVSTj-yALjbZE9lxItHGaIkwYChUVfQecW7BHIJIAhE3Mg__; _strava_idcf=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NjEyMDM1OTIsImlhdCI6MTc2MTExNzE5MiwiYXRobGV0ZUlkIjoxNDI5NjA5OTcsInRpbWVzdGFtcCI6MTc2MTExNzE5Mn0.nd3Yo0wp9XbRUHpkswEF9R-1DEn49W5b5dX9861KqXM; _strava_CloudFront-Expires=1761203592000"

analyze_cookie_expiry(cookie_string)