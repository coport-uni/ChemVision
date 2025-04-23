# 개발환경 세팅
```bash
# raspi I2C 활성화!
sudo raspi-config
# ARM 버전 Conda 다운로드 후 설치
sh Anaconda3-2024.10-1-Linux-aarch64.sh
sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED
# add to bashrc
export PATH=~/anaconda3/bin:$PATH
conda init
conda create -n cv python=3.10
conda activate cv
```

# 모터제어
* https://github.com/adafruit/Adafruit_CircuitPython_MotorKit
* https://learn.adafruit.com/circuitpython-on-raspberrypi-linux
* https://velog.io/@jjanmo/%ED%8C%8C%EC%9D%B4%EC%8D%AC%EC%97%90%EC%84%9C-switch%EB%AC%B8%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94-%EB%B0%A9%EB%B2%95 
```bash
pip install adafruit-circuitpython-motorkit
pip install lgpio
pip install --upgrade gradio
```

```python
from adafruit_motorkit import MotorKit
import time
class ChemVision():

    def __init__(self):
        self.kit = MotorKit()
        print("hello world")

    def cameraRGB(self):
        print("hello world")

    def motor_control(self, id, power):
        if id == 1 and -1 <= power <= 1 :
            self.kit.motor1.throttle = power
        elif id == 2 and -1 <= power <= 1:
            self.kit.motor2.throttle = power
        elif id == 3 and -1 <= power <= 1:
            self.kit.motor3.throttle = power
        elif id == 4 and -1 <= power <= 1:
            self.kit.motor4.throttle = power
        else:
            print("Invalid id")

def main():
    cv = ChemVision()
    cv.motor_control(4, 1)
    time.sleep(5)
    cv.motor_control(4, 0)
    
if __name__ == "__main__":
    main()
```
# 카메라제어
* https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4
* https://www.raspberrypi.com/documentation/accessories/camera.html
* https://chick-it.tistory.com/19
```bash
sudo apt-get update
sudo apt-get full-upgrade
rpicam-hello --list-cameras

# 카메라 정상 확인후
sudo apt update && sudo apt upgrade 
sudo apt install libcap-dev libatlas-base-dev ffmpeg libopenjp2-7 
sudo apt install libcamera-dev 
sudo apt install libkms++-dev libfmt-dev libdrm-dev
pip install --upgrade pip 
pip install wheel 
pip install rpi-libcamera rpi-kms picamera2
conda install -c conda-forge
```

```python
from adafruit_motorkit import MotorKit
from picamera2 import Picamera2
import time
import cv2
import os

class ChemVision():

    def __init__(self):
        self.kit = MotorKit()
        self.picam = Picamera2()
    
    def cameraRGB(self):
        self.picam.start()
        output = self.picam.capture_array()

        return output
        # cv2.imwrite("test.jpg", output)

    def motor_control(self, id, power):
        if id == 1 and -1 <= power <= 1 :
            self.kit.motor1.throttle = power
        elif id == 2 and -1 <= power <= 1:
            self.kit.motor2.throttle = power
        elif id == 3 and -1 <= power <= 1:
            self.kit.motor3.throttle = power
        elif id == 4 and -1 <= power <= 1:
            self.kit.motor4.throttle = power
        else:
            print("Invalid id")

def main():
    cv = ChemVision()
    cv.cameraRGB()
    # cv.motor_control(4, 1)
    # time.sleep(5)
    # cv.motor_control(4, 0)
    
if __name__ == "__main__":
    main()
```
![[Pasted image 20250415174740.png]](https://github.com/coport-uni/ChemVision/blob/main/Pasted%20image%2020250415174740.png)
![[Pasted image 20250415175928.png]](https://github.com/coport-uni/ChemVision/blob/main/Pasted%20image%2020250415175928.png)
# 총개발

```python
from adafruit_motorkit import MotorKit
from picamera2 import Picamera2
from tqdm import tqdm
import numpy as np
import gradio as gr
import time
import cv2
import os
import threading

grgb = []

class ChemVision():

    def __init__(self):
        self.kit = MotorKit()
        self.picam = Picamera2()
        config = self.picam.create_still_configuration({"size":(640,480),'format': 'RGB888'})
        self.picam.start(config)
    
    def calchist(self, a):
        colors, count = np.unique(a.reshape(-1,a.shape[-1]), axis=0, return_counts=True)
        return colors[count.argmax()], count.argmax() 

    def cameraRGB(self):
        output = self.picam.capture_image()
        output_a = np.array(output)
        value, number = self.calchist(output_a)
        number = round((number/(640*480))*100,0)
        text = f"R,G,B Value is {value}, and percentage is {number}%"
        return output, text

    def threadRGB(self):
        global grgb
        while True: 
            output = self.picam.capture_image()
            output_a = np.array(output)
            value, number = self.calchist(output_a)
            grgb = value
            time.sleep(0.5)
            print(grgb)

    def motor_control(self, mid, power):
        if mid == 1 and -1 <= power <= 1 :
            self.kit.motor1.throttle = power
            message = f"Motor {mid} working on {power}"
        elif mid == 2 and -1 <= power <= 1:
            self.kit.motor2.throttle = power
            message = f"Motor {mid} working on {power}"
        elif mid == 3 and -1 <= power <= 1:
            self.kit.motor3.throttle = power
            message = f"Motor {mid} working on {power}"
        elif mid == 4 and -1 <= power <= 1:
            self.kit.motor4.throttle = power
            message = f"Motor {mid} working on {power}"
        else:
            message = "Invalid mid"

        # print(message)
        return message

    def program1(self):

        # Test1: Reach target point
        print("Test1: Reach target point")
        global grgb
        time_100ml = 110 # Second
        time_200ml = 220

        # target_rgb = [170,120,230]
        target_rgb = [22,21,30]
        error_margin = 30
        i = 0

        # Blue
        self.motor_control(2, 1)
        for i in tqdm(range(time_100ml),desc="Waiting_to_fill_blue"):
            time.sleep(1)

        self.motor_control(2, 0)

        # Red
        i = 0
        while True:
            if len(grgb) == 0:
                print("waiting_valid_value")
            else:
                if target_rgb[0] - error_margin/2 < grgb[0] < target_rgb[0] + error_margin/2 and target_rgb[1] - error_margin/2 < grgb[1] < target_rgb[1] + error_margin/2 and target_rgb[2] - error_margin/2 < grgb[2] < target_rgb[2] + error_margin/2:
                    print("Job_complete")
                    self.motor_control(3, 0)

                    # Output
                    self.motor_control(4, -1)
                    for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                        time.sleep(1)

                    self.motor_control(4, 0)
                    exit()

                elif i > 97:
                    print("Job_complete_timeover")
                    self.motor_control(3, 0)

                    # Output
                    self.motor_control(4, -1)
                    for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                        time.sleep(1)

                    self.motor_control(4, 0)
                    exit()

                else:
                    self.motor_control(3, 1)
                    time.sleep(1)
                    i = i + 1
        
    def program2(self):
        # Test 2: Reach reddish target point
        print("Test 2: Reach reddish target point")
        global grgb
        time_100ml = 110 # Second
        time_200ml = 220

        # target_rgb = [170,120,230]
        # reddish_target_rgb = [22+40,21,30]
        reddish_target_rgb = [130,75,120]
        target_rgb = reddish_target_rgb
        error_margin = 30
        i = 0

        # Blue
        print("waiting_blue")
        self.motor_control(2, 1)
        time.sleep(time_100ml)
        # for i in tqdm(range(time_100ml),desc="Waiting_to_fill_blue"):
        #     time.sleep(1)
        self.motor_control(2, 0)

        # Red
        print("waiting_red")
        i = 0
        while True:
            if len(grgb) == 0:
                print("waiting_valid_value")
            else:
                if target_rgb[0] - error_margin/2 < grgb[0] < target_rgb[0] + error_margin/2 and target_rgb[1] - error_margin/2 < grgb[1] < target_rgb[1] + error_margin/2 and target_rgb[2] - error_margin/2 < grgb[2] < target_rgb[2] + error_margin/2:
                    print("Job_complete")
                    self.motor_control(3, 0)

                    # Output
                    self.motor_control(4, -1)
                    time.sleep(time_100ml)
                    # for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                    #     time.sleep(1)
                    self.motor_control(4, 0)
                    exit()

                elif i > 97 + 50:
                    print("Job_complete_timeover")
                    self.motor_control(3, 0)

                    # Output
                    self.motor_control(4, -1)
                    time.sleep(time_100ml)
                    # for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                    #     time.sleep(1)
                    self.motor_control(4, 0)
                    exit()

                else:
                    self.motor_control(3, 1)
                    time.sleep(1)
                    i = i + 1
    
    def program3(self):
        # Test 3: Simultaneously control 2 liquid
        print("Test 3: Simultaneously control 2 liquid")
        
        global grgb
        time_100ml = 110 # Second
        time_200ml = 220

        # target_rgb = [170,120,230]
        # reddish_target_rgb = [22+40,21,30]
        # reddish_target_rgb = [130,75,120]
        # target_rgb = reddish_target_rgb
        # 2 => blue 3 => red 4 => output
        target_rgb = [75,60,70]
        error_margin = 30

        # Red & Blue
        print("waiting_red")
        i = 0
        while True:
            if len(grgb) == 0:
                print("waiting_valid_value")
            else:
                if target_rgb[0] - error_margin/2 < grgb[0] < target_rgb[0] + error_margin/2 and target_rgb[1] - error_margin/2 < grgb[1] < target_rgb[1] + error_margin/2 and target_rgb[2] - error_margin/2 < grgb[2] < target_rgb[2] + error_margin/2:
                    print("Job_complete")
                    self.motor_control(3, 0)
                    self.motor_control(2, 0)

                    # Output
                    self.motor_control(4, -1)
                    time.sleep(time_100ml)
                    # for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                    #     time.sleep(1)
                    self.motor_control(4, 0)
                    exit()

                elif i > 97:
                    self.motor_control(3, 0)
                    time.sleep(time_100ml-97)
                    self.motor_control(2, 0)
                    print("Job_complete_timeover")

                    # Output
                    self.motor_control(4, -1)
                    time.sleep(time_100ml)
                    # for i in tqdm(range(time_100ml),desc="Waiting_to_empty"):
                    #     time.sleep(1)
                    self.motor_control(4, 0)
                    exit()

                else:
                    self.motor_control(3, 1)
                    self.motor_control(2, 1)
                    time.sleep(1)
                    i = i + 1
    
    def gui_launcher(self):
        
        with gr.Blocks() as demo:

            gr.Markdown("ChemVisionDemo-motor")
            mid = gr.Dropdown([2, 3, 4],label="모터 ID")
            mpower = gr.Slider(-1,1, value=0, step=0.5,label="모터 Power")
            txt_3 = gr.Textbox(value="",label="실행 결과")
            mbutton = gr.Button(value="실행")
            mbutton.click(self.motor_control, inputs=[mid, mpower], outputs=[txt_3])

            gr.Markdown("ChemVisionDemo-vision")
            output_img = gr.Image()
            txt_3 = gr.Textbox(value="",label="감지된 RGB Value")
            vbutton = gr.Button(value="RGB값 확인")
            vbutton.click(self.cameraRGB, inputs=[], outputs=[output_img, txt_3])

            gr.Markdown("ChemVisionDemo-program")
            vbutton = gr.Button(value="1번 실험 시작")
            vbutton.click(self.program1, inputs=[], outputs=[])
            vbutton = gr.Button(value="2번 실험 시작")
            vbutton.click(self.program2, inputs=[], outputs=[])
            vbutton = gr.Button(value="3번 실험 시작")
            vbutton.click(self.program3, inputs=[], outputs=[])

        demo.launch(share=True)
        # demo.launch()

def main():
    cv = ChemVision()

    th1 = threading.Thread(target=cv.threadRGB)
    th1.start()
    # th2 = threading.Thread(target=cv.program1)
    # th2.start()
    # th2 = threading.Thread(target=cv.program2)
    # th2.start()
    cv.gui_launcher()
    
if __name__ == "__main__":
    main()
```
