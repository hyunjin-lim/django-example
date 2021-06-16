# django-example

Version
```
Python 3.9.x
Django==3.1.4
djangorestframework==3.12.2
mysql-connector-python==8.0.23
```

1. install
   ```
   //가상화 설치 
   python -m venv .venv
   
   . .venv/bin/activate
   
   pip install --upgrade pip
   
   //패키지 설치
   pip install -r requirements.txt
   
   //패키지 export
   pip freeze > requirements.txt
   
   python manage.py migrate
   ```
2. data sample
    ```
   1. fixture 사용
   // export
   python manage.py dumpdata [app_name].[model.name] --indent [INDENT] > [fixture_name].json
   // import
   python manage.py loaddata [app_name]/fixtures/[fixture_name].json
    ```
 
3. authenticate
   ```
   1. JWT token 
   2. session
   3. redis
   ```
  
4. Example
   ```
   1. backend user // 로그인 authenticate 추가
   
   AUTHENTICATION_BACKENDS = (
      'apps.users.user_backend.UserBackend',
      'django.contrib.auth.backends.ModelBackend',
   )
   
   2. Api Authentication 
   REST_FRAMEWORK = {
      ...
      'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.core.redis_auth.RedisAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'apps.core.jwt_auth.JSONWebTokenAuthentication',
      ),
      ...
   }
   
   ```