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