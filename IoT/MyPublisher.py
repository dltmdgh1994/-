import paho.mqtt.publish as publish
import cv2

img = cv2.imread('C:/Users/s_csmscox/jupyterSave/eye_blink/face4.jpg')
bts = cv2.imencode('.jpg', img)[1]
bts = bts.tostring()

publish.single("mydata/img", bts, hostname="3.35.174.45")
