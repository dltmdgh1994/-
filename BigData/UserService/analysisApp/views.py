from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User,Co2,Eye,Emotion
from .UserSerializer import UserSerializer
import json
import hashlib
import pandas as pd
from datetime import datetime, timedelta


# from django.core.context_processors import csrf
# 사용자 정보 수정 (시리얼 번호 변경)
@api_view(["PUT"])
def user_data_update(request):
    user_id = request.data['user_id']
    serial_no1 = request.data['serial_no1']
    user = User.objects.get(user_id = user_id)
    user.serial_no1 =serial_no1
    try:
        user.save()
        return Response({"result":True})
    except Exception:
        return Response({"result":False})


# 회원 가입
@api_view(['POST'])
def createUser(request):
    user_pwd = request.data['user_pwd'].encode()
    encode_pwd = hashlib.sha256(user_pwd).hexdigest()
    json_data = request.data
    json_data['user_pwd']=encode_pwd
    # 역 직렬화
    serializer = UserSerializer(data = json_data)

    if(serializer.is_valid()):
        print("성공")
        serializer.save()
        return Response({'success':True})
    else:
        print("실패")
        return Response({'success':False})
   

#사용자 아이디 중복 체크
@api_view(['GET'])
def userIdcheck(request,userid):
    user_id =userid
    try:
        userIdcheck = User.objects.get(user_id=user_id)
        return Response({'result':False})
    except Exception:
        return Response({'result':True})


# 시리얼 번호 중복 체크
@api_view(['GET'])
def serial_no_check(request,serial_no1):
    serial_no1=serial_no1
    try:
        serialcheck = User.objects.get(serial_no1=serial_no1)
        return Response({'result':False})
    except Exception:
        return Response({'result':True})


# 로그인 
@api_view(['POST'])
def login(request):
    # body에 있는 회원의 id 및 pwd 가져오기
    json_param = json.loads(request.body)
    user_id = json_param['user_id']
    userpwd = json_param['user_pwd']
    # 회원의 비밀번호 encode 및 hash로 변환해 암호화
    user_pwd = userpwd.encode()
    encode_pwd = hashlib.sha256(user_pwd).hexdigest()
    try:
        idcheck = User.objects.get(user_id = user_id)
        # 아이디 존재
        print(idcheck.user_pwd)
        # 암호화한 회원의 비밀번호 조회
        if encode_pwd == idcheck.user_pwd:
            print("로그인 성공")
            return Response({'message':'성공','user_id':user_id,'success':True})
        else:
            # print("로그인 실패1")
            return Response( {'message':'비밀번호','success':False})
    except Exception:
        print("로그인 실패2")
        return Response({'message':'아이디','success':False})


# 회원 운전 위험수치 가져오기
@api_view(['GET'])
def yesterdayData(request, userid):
    user_id = userid
    # 사용자의 ID를 가지고 해당 사용자의 데이터 구하기
    eye = Eye.objects.filter(user_id=user_id)
    emotion = Emotion.objects.filter(user_id=user_id)

    # 1. eye 전처리
    eye_time = []
    eye_issleep = []
    for a in eye:
        eye_time.append(a.time)
        eye_issleep.append(a.is_sleep)
    df_eye = pd.DataFrame({'time': eye_time, 'is_sleep': eye_issleep})
    print(df_eye)

    # 1-1. 시간 단위 쪼개기
    print(df_eye.info())
    df_eye['year'] = df_eye['time'].dt.year
    df_eye['month'] = df_eye['time'].dt.month
    df_eye['day'] = df_eye['time'].dt.day
    df_eye['hour'] = df_eye['time'].dt.hour
    df_eye['minute'] = df_eye['time'].dt.minute
    df_eye['second'] = df_eye['time'].dt.second
    print(df_eye)

    # 1-2. 어제의 날짜 데이터만 추출
    yesterday = datetime.today() - timedelta(1)
    print(yesterday)
    df_eye = df_eye.loc[df_eye.year == yesterday.year]
    df_eye = df_eye.loc[df_eye.month == yesterday.month]
    df_eye = df_eye.loc[df_eye.day == yesterday.day]
    print(df_eye)
    print(df_eye.info())

    # 1-3.졸음별 갯수 세기
    print(df_eye.groupby('is_sleep', as_index=False).size())
    df_sleep = pd.DataFrame(df_eye.groupby('is_sleep', as_index=False).size())
    print(df_sleep)
    print(df_sleep.info())
    df_sleep.columns = ['is_sleep', 'count']

    # 2. emotion 전처리
    emotion_time = []
    emotion_emotion = []
    for a in emotion:
        emotion_time.append(a.time)
        emotion_emotion.append(a.emotion)
    df_emotion = pd.DataFrame({'time': emotion_time, 'emotion': emotion_emotion})
    # print(df_emotion)

    # 2-1. 시간 단위 쪼개기
    # print(df_emotion.info())
    df_emotion['year'] = df_emotion['time'].dt.year
    df_emotion['month'] = df_emotion['time'].dt.month
    df_emotion['day'] = df_emotion['time'].dt.day
    df_emotion['hour'] = df_emotion['time'].dt.hour
    df_emotion['minute'] = df_emotion['time'].dt.minute
    df_emotion['second'] = df_emotion['time'].dt.second
    # print(df_emotion)

    # 2-2. 어제의 날짜 데이터만 추출
    yesterday = datetime.today() - timedelta(1)
    # print(yesterday)
    df_emotion = df_emotion.loc[df_emotion.year == yesterday.year]
    df_emotion = df_emotion.loc[df_emotion.month == yesterday.month]
    df_emotion = df_emotion.loc[df_emotion.day == yesterday.day]
    # print(df_emotion)

    # 2-3.졸음별 갯수 세기
    print(df_emotion.groupby('emotion', as_index=False).size())
    df_emo = pd.DataFrame(df_emotion.groupby('emotion', as_index=False).size())
    print(df_emo)
    print(df_emo.info())

    df_emo.columns = ['emotion', 'count']

    json_list = {
        'Sleep' : df_sleep,
        'Emotion' : df_emo,
    }

    return Response(json_list)

@api_view(['GET'])
def co2MeanData(request, userid):
    user_id = userid
    print(user_id)

    # 사용자의 ID를 가지고 해당 사용자의 데이터 구하기
    co2 = Co2.objects.filter(user_id=user_id)

    #  전처리
    time = []
    amount = []
    for a in co2:
        time.append(a.time)
        amount.append(a.amount)
    df_co2 = pd.DataFrame({'time': time, 'amount': amount})
    print(df_co2)

    # 1. 시간 단위 쪼개기
    print(df_co2.info())
    df_co2['year'] = df_co2['time'].dt.year
    df_co2['month'] = df_co2['time'].dt.month
    df_co2['day'] = df_co2['time'].dt.day
    df_co2['hour'] = df_co2['time'].dt.hour
    df_co2['minute'] = df_co2['time'].dt.minute
    df_co2['second'] = df_co2['time'].dt.second
    print(df_co2)

    # 2. 시간대별 이산화탄소 평균 구하기
    dfCo2 = pd.DataFrame(df_co2.groupby('hour', as_index=False).mean())
    dfCo2 = dfCo2[['hour', 'amount']]
    print(dfCo2)
    print(dfCo2.info())
    dfCo2.columns = ['hour', 'co2_mean']

    json_list = {
        'Co2Mean' : dfCo2,
    }

    return Response(json_list)