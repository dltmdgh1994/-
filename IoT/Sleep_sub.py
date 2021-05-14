import time
import threading
import paho.mqtt.client as mqtt
# import RPi.GPIO as GPIO
from tensorflow.keras.models import load_model
import tensorflow as tf
import cv2
import dlib
import numpy as np
from imutils import face_utils
from matplotlib import pyplot as plt
from PIL import Image


# 이산화탄소 subscribe
class MyMqtt_Sub:

    def __init__(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect("3.35.174.45", 1883, 60)  # EC2 mqttbroker 주소 
        ##############################
        #GPIO 설정
        # GPIO.setmode(GPIO.BCM)
     
        ############################
        ############################
        #AI 설정
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(
            'shape_predictor_68_face_landmarks.dat 경로')
        self.img_size = (32, 32)

        self.model = load_model('C:/Users/s_csmscox/jupyterSave/eye_blink/eye_blink_CNN_ImgGen1_FT.h5')
        self.origin_img = None

        self.eye_blink = None
        self.co2 = None
        self.motion = None

        ###########################
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("connect.." + str(rc))
        if rc == 0:
            img_data = client.subscribe("mydata/img")
            Co2_data = client.subscribe("mydata/Co2")
        else:
            print("연결실패")

    def on_message(self, client, userdata, msg):

        myval = msg.payload.decode("utf-8")

        # 이미지인지 Co2인지 확인
        myval = str(msg.payload)
        print(myval)
        # print(myval)
        # print(msg.topic + "----" + str(myval))

        # 움직임 탐지 방식 => 원본 이미지와 새로운 이미지 사이의 달라진 픽셀 측정
        # 첫 이미지를 원본 이미지로??? 아니면 주기적으로 원본 이미지 수집 => 게이트에서 판별???

        if type(myval) == str:
            # reshape 해줘야 한다.
            myval = np.fromstring(myval, np.uint8)
            myval = myval.reshape(-1, 1)
            myval = cv2.imdecode(myval, cv2.IMREAD_COLOR)

            if self.origin_img is None:
                self.origin_img = myval
                cv2.imshow('image', self.origin_img)
            else:
                compare_img = myval
                # 이산화탄소 데이터 / 이미지 파일 구분?
                faces = self.detector(myval)

                for face in faces:
                    shapes = self.predictor(compare_img, face)
                    shapes = face_utils.shape_to_np(shapes)

                    eye_img_l, eye_rect_l = self.crop_eye(compare_img, eye_points=shapes[36:42])
                    eye_img_r, eye_rect_r = self.crop_eye(compare_img, eye_points=shapes[42:48])

                    eye_img_l = cv2.resize(eye_img_l, dsize=self.img_size)
                    eye_img_r = cv2.resize(eye_img_r, dsize=self.img_size)

                    # 왼쪽 눈
                    eye_input_l = eye_img_l.copy().reshape((1, self.img_size[1], self.img_size[0], 3)).astype(
                        np.float32)
                    eye_input_l = eye_input_l / 255

                    pred_l = self.model.predict(eye_input_l)
                    pred_l = np.argmax(pred_l)

                    # 오른쪽 눈
                    eye_input_r = eye_img_r.copy().reshape((1, self.img_size[1], self.img_size[0], 3)).astype(
                        np.float32)
                    eye_input_r = eye_input_r / 255

                    pred_r = self.model.predict(eye_input_r)
                    pred_r = np.argmax(pred_r)

                    # 눈에 직사각형 그리기
                    # cv2.rectangle(compare_img, pt1=tuple(eye_rect_l[0:2]), pt2=tuple(eye_rect_l[2:4]),
                    #               color=(255, 255, 255), thickness=2)
                    # cv2.rectangle(compare_img, pt1=tuple(eye_rect_r[0:2]), pt2=tuple(eye_rect_r[2:4]),
                    #               color=(255, 255, 255), thickness=2)
                    #
                    # cv2.putText(compare_img, str(pred_l), tuple(eye_rect_l[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    #             (255, 255, 255), 2)
                    # cv2.putText(compare_img, str(pred_r), tuple(eye_rect_r[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    #             (255, 255, 255), 2)

                    cv2.imshow('image', compare_img)

                    # 두 눈 다 감은 경우 졸음으로 예측
                    if pred_l == 0 and pred_r == 0:
                        n_count += 1
                    else:
                        n_count = 0
                        self.eye_blink = 0

                    # n_count가 10 초과하면 경고 메세지
                    if n_count > 10:
                        # cv2.putText(compare_img, "Wake up!(eye_blink)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        #             (0, 0, 255), 2)
                        print("Wake up!(eye_blink)")
                        self.eye_blink = 1

                    # 원본과 움직인 이미지를 비교해서 mse가 일정 이상일 시 움직인것으로 판단
                    mse_val = self.mse(self.origin_img, compare_img)

                    if mse_val > 2000:
                        # cv2.putText(compare_img, "Wake up!(movement)", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        #             (255, 0, 0), 2)
                        print("Wake up!(movement)")
                        self.motion = 1
                    else:
                        self.motion = 0

        elif myval == 'Co2_data':
            if myval > 1500:
                print("Wake Up!(Co2)")
                self.co2 = 1
            else:
                self.co2 = 0

        self.sleep_gate(self, self.eye_blink, self.motion, self.co2)

    @staticmethod
    def sleep_gate(self, eye_blink, motion, co2):
        if eye_blink == 1 and motion == 1 and co2 == 1:
            print("졸았다!!!!!")
        else:
            print("안 졸았다!!")

    @staticmethod
    def mse(self, img, compare_img):
        err = np.sum((img.astype("float") - compare_img.astype("float")) ** 2)
        err /= float(img.shape[0] * compare_img.shape[1])
        return err

    def crop_eye(self, img, eye_points):
        x1, y1 = np.amin(eye_points, axis=0)
        x2, y2 = np.amax(eye_points, axis=0)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        w = (x2 - x1) * 1.2
        h = w * self.img_size[1] / self.img_size[0]

        margin_x, margin_y = w / 2, h / 2

        min_x, min_y = int(cx - margin_x), int(cy - margin_y)
        max_x, max_y = int(cx + margin_x), int(cy + margin_y)

        eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int)

        eye_img = img[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]

        return eye_img, eye_rect


if __name__ == "__main__":
    try:
        mymqtt = MyMqtt_Sub()
    except KeyboardInterrupt:
        print("종료")
        # GPIO.cleanup()
