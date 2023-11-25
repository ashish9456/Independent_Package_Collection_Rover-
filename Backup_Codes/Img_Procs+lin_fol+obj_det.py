import cv2
import RPi.GPIO as IO
import time

#Setting up the ultrasonic sensor start
TRIG=23
ECHO=24
IO.setmode(IO.BCM)
#Setting up the ultrasonic sensor end

IO.setwarnings(False)
IO.setmode(IO.BCM)

IO.setup(2,IO.IN) #GPIO 2 -> Left IR out
IO.setup(3,IO.IN) #GPIO 3 -> Right IR out
IO.setup(4,IO.OUT) #GPIO 4 -> Motor 1 terminal A
IO.setup(14,IO.OUT) #GPIO 14 -> Motor 1 terminal B
IO.setup(17,IO.OUT) #GPIO 17 -> Motor Left terminal A
IO.setup(18,IO.OUT) #GPIO 18 -> Motor Left terminal B


#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "/home/pi/Desktop/Object_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Desktop/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Desktop/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    
    return img,objectInfo


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img,0.48,0.15,objects=['person','bicycle','car','motorcycle','traffic light'
        ,'fire hydrant','stop sign','dog','cat',])
        
        #Object detection code starts
        print("###OBJECT DETECTION ACTIVE###")
        print("Distance measurement in progress")
        IO.setup(TRIG,IO.OUT)
        IO.setup(ECHO,IO.IN)
        IO.output(TRIG,False)
        print("Waiting for sensor to settle")
        time.sleep(0.2)
        IO.output(TRIG,True)
        time.sleep(0.00001)
        IO.output(TRIG,False)
        while IO.input(ECHO)==0:
            pulse_start=time.time()
        while IO.input(ECHO)==1:
            pulse_end=time.time()
        pulse_duration=pulse_end-pulse_start
        distance=pulse_duration*17150
        distance=round(distance,2)
        print("Distance:",distance,"cm")
        time.sleep(2)
    
    #Object Detection code ends
        
        #Rover motors code starts:
        if(len(objectInfo)!=1 and distance>30):
            if(IO.input(2)==True and IO.input(3)==True): #both while move forward     
                IO.output(4,True) #1A+
                IO.output(14,False) #1B-
                IO.output(17,True) #2A+
                IO.output(18,False) #2B-
            
            elif(IO.input(2)==False and IO.input(3)==True): #turn right  
                IO.output(4,True) #1A+
                IO.output(14,False) #1B-
                IO.output(17,True) #2A+
                IO.output(18,True) #2B-

            elif(IO.input(2)==True and IO.input(3)==False): #turn left
                IO.output(4,True) #1A+
                IO.output(14,True) #1B-
                IO.output(17,True) #2A+
                IO.output(18,False) #2B-
                
            elif(IO.input(2)==False and IO.input(3)==False): #stay still
                IO.output(4,True) #1A+
                IO.output(14,True) #1B-
                IO.output(17,True) #2A+
                IO.output(18,True) #2B-
        
        else:  #stay still
            IO.output(4,True) #1A+
            IO.output(14,True) #1B-
            IO.output(17,True) #2A+
            IO.output(18,True) #2B-'''
        #Rover motor code ends
            
        if len(objectInfo) == 1:
            print("Image processing active!")
            print("Image processing detected a target")
            print("Stopping the rover until clearance...")    
        cv2.imshow("Output",img)
        cv2.waitKey(1)
        
        
    
#Code for one US sensor only. Other 3 sensors interfacing to be done.
