#!usr/bin/python

import cv2 as cv
import os
import sys

cap = cv.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
#cap.set(3, 1280)
#cap.set(4, 720)
#cap.set(cv.CAP_PROP_FRAME_WIDTH, 680)
#cap.set(cv.CAP_PROP_FRAME_HEIGHT, 680)

# initiate tracker
tracker = cv.TrackerCSRT_create()

# read initial frame for customized bounding box
ret, frame = cap.read()
bbox = cv.selectROI('Tracking', frame, False)
initial_txt = 'Please draw a bounding box'
cv.putText(frame, initial_txt, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv.LINE_AA)

# initialzie tracker using the bounding box
tracker.init(frame, bbox)

def drawBbox(frame, bbox):
    """
    A function that draws boudning box on a frame based on the bbox dimensions.
    """
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    cv.rectangle(frame, (x, y), ((x + w), (y+h)), (255, 0, 0), 2, 1)

# directry to output latest_label.txt file and raw images
PATH = '../../data/raw/'

# placeholder for object class
if len(sys.argv) == 1:
    print("Please enter the name for the object.")
    exit()

obj = str(sys.argv[1])

# create data folder for output frames
output_path = PATH + obj
if not os.path.exists(output_path):
    os.makedirs(output_path)
else:
    print("An obejct with the same name exists; please use a different name and try again:)")
    exit()

# write the class name to latest_label.txt
txt_label_file_path = PATH + 'latest_label.txt'
with open(txt_label_file_path, 'w') as file:
    file.write(obj)

i = 0
# capture video from camera
while(True):

    # Capture frame-by-frame
    ret, frame = cap.read()

    # get bbox and updates tracker
    ret, bbox = tracker.update(frame)

    if ret:
        # draw bbox if traking succeeded
        drawBbox(frame, bbox)
    else:
        # print missing if not
        cv.putText(frame, 'lost', (100, 145), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

    # display status
    x, y, w, h = round(bbox[0], 1), round(bbox[1], 1), round(bbox[2], 1), round(bbox[3], 1)
    txt = 'Capturing training samples'
    txt_xywh = 'x:{}  y:{}  w:{}  h:{}'.format(x, y, w, h)
    cv.putText(frame, txt, (50, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv.LINE_AA)
    cv.putText(frame, txt_xywh, (50, 55), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)

    # write frame to raw images
    cv.imwrite(output_path+"/"+obj+"_"+str(i)+".jpg", frame)
    i += 1

    # write bbox dimension to file
    # file path for bbox dimensions
    txt_dim_file_path = output_path + '/bbox.txt'
    with open(txt_dim_file_path, 'a+') as file:
        file.write(' '.join(str(s) for s in bbox) + '\n')

    cv.imshow('output_', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
