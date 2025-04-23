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