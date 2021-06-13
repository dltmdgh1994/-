# Django Rest Framework API



## 제작한 팀원

**김혜림** 

​	사용자 데이터 전처리 및 분석

**김성수**

​	사용자 서비스 작성 및 빌드



## 설명

안드로이드로 부터 사용자 인증과 더불어 사용자 데이터를 전처리 및 분석하여 API로 제공



##  사용된 라이브러리

requirements.txt 참조

``` tex
asgiref==3.3.4
DateTime==4.3
Django==3.2.4
django-sslserver==0.22
djangorestframework==3.12.4
gunicorn==20.1.0
mysqlclient==2.0.3
numpy==1.20.3
pandas==1.2.4
python-dateutil==2.8.1
pytz==2021.1
six==1.16.0
sqlparse==0.4.1
zope.interface==5.4.0
```

**해당 서버를 실행하기 전 insatall** 

`` pip3 install -r requirements.txt ``



### 주요 라이브러리 설명

1. djangorestframework 

   Rest API 통신을 하기 위한 라이브러리

   setting.py 의 INSATALLED_APPS에 적용

   ```python
   INSTALLED_APPS = [
       ....
       'rest_framework',
   ]
   ```

   

2. mysqlclient 

   서버에 빌드된 mariadb에 access 하기 위한 Engine

   settings.py의 DATABASES에 적용

   ```python
   DATABASES = {
       'default': {
           # 'ENGINE': 'django.db.backends.sqlite3',
           # 'NAME': BASE_DIR / 'db.sqlite3',
           'ENGINE' : 'django.db.backends.mysql',
           'NAME' : 'DATABASE', # 테이블들이 들어갈 데이터베이스 이름
           'USER' : 'USER_ID', #mariadb에서 생성한 user (root는 쓰지 말 것!!) 
           'PASSWORD' :'PASSWORD',
           'HOST' : 'IP',#mariadb가 빌드된 서버의 IP
           'PORT' : 'PORT' # mariadb가 빌드된 서버의 prot 번호
       }
   }
   ```

   

3. django-sslserver 

   안드로이드와 rest 통신을 하기위해서는 https 통신이 필요하기 때문에 django서버를 https로 실행시키기 위한 라이브러리

   setting.py 의 INSATALLED_APPS에 적용

   ``` python
   INSTALLED_APPS = [
       ....
       'sslserver',
   ]
   ```

   **실행 방법**

   ``python manage.py runsslserver``

   

4. gunicorn (해당 프로젝트에서는 사용하지 못함)

   EC2(t2)에 django를 running시키기 위한 웹 서버 게이트웨이 인터페이스 HTTP 서버

   

5. pandas

   데이터 조작 및 분석을 위한 python 소프트웨어 라이브러리

   

6. Datetime

   시간대 별로 데이터를 분석하고 전처리 하기위해 사용한 라이브러리





## 주요 기능 



### 사용자 API (모든 return 값은 Json 형태로 반환)

1. **로그인 (POST)**

   아이디와 비밀번호를 mariadb에 있는 사용자 정보와 비교하여 json형태로 리턴 

   (여기서 비밀번호는 hash로 인코딩후 mariadb에 있는 비밀번호와 비교)

   **return**

   ``` python
   ## 아이디가 존재하지 않는 경우
   {
       'message':'아이디',
       'success':False
   }
   
   ## 비밀번호가 틀릴경우 
   {
       'message':'비밀번호',
       'success':False
   }
   
   ## 로그인 성공
   {
       'message':'성공',
       'user_id':user_id,
       'success':True
   }
   ```

   

2. **회원가입 (POST)**

   사용자 정보를 json 형태로 받아 **비밀번호만 hash로 암호화** 

   해당 json데이터를 역 직렬화 한 후 mariadb에 저장 

   **return**

   ``` python
   ## DB에 저장이 성공적으로 이뤄질 경우
   {
       'success':True
   }
   
   ## DB에 저장을 못한 경우
   {
       'success':False
   }
   ```

   

3. **아이디 중복 check (GET)**

   사용자가 회원 가입을 할경우 유니크한 id를 만들기 위해 DB의 아이디를 조회해 중복 chek

   **return**

   ``` python
   ## 아이디가 존재한다면 
   {
       'result':False
   }
   
   ## 아이디가 존재하지 않다면
   {
       'result':True
   }
   ```

   

4. **시리얼 번호 중복 check (GET)**

   프로젝트에서 생성한 고유 IoT 시리얼 번호를 등록할 경우 사용자별 시리얼 번호가 중복되는 것을 방지하기 위한 API

   **return**

   ``` python
   ## 시리얼번호가 존재한다면 
   {
       'result':False
   }
   
   ## 시리얼번호가 존재하지 않다면
   {
       'result':True
   }
   ```

   

5. **사용자 시리얼 번호 변경 (PUT)**

   사용자의 IoT 장비가 고장으로 변경해야 할 경우를 대비해 시리얼 번호를 update할 수 있도록 한 API

   **return**

   ```python
   ## 시리얼번호변경을 못한 경우 
   {
       'result':False
   }
   
   ## 시리얼번호를 성공적으로 변경한 경우
   {
       'result':True
   }
   ```

   

###  사용자 데이터 분석 및 전처리 API









##  EC2에 빌드 방법 

1. 로컬에 있는 UserService와 Dockerfile 을 EC2(t2)에 Copy  ( 해당 방법에는 mobaxterm을 사용)

   **Dockerfile**

   ```dockerfile
   FROM python:3 ## 기본 베이스 이미지
   WORKDIR /usr/src/app
   
   ## Install packages
   RUN apt-get update
   RUN apt-get install -y vim # 혹시모를 수정을 위해 vim 설치
   COPY requirements.txt ./ #EC2에 있는 requirements.txt 파일복사
   RUN pip3 install -r requirements.txt
   COPY UserService . #UserService 복사
   EXPOSE 8000 #포트 포워딩 8000
   CMD ["python", "manage.py", "runsslServer", "--host=0.0.0.0", "-p 8000"] #실행 명령어
   # CMD ["gunicorn", "--workers=5" ,"--bind", "0.0.0.0:8000", "UserService.wsgi:application"] 
   ```

2.  Dockerfile을 실행해 docker image 생성 

   ```shell
   docker build -t '도커아이디/이미지 이름:버전' . 
   ```

3. 해당 이미지를 기반으로 컨테이너 생성

   ```shell
   docker run --name '컨테이너 이름' -d -p 8000:8000 '이미지 이름'
   ```



