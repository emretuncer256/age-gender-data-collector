from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import cv2

box_color = (55, 255, 75)
male_color = (220, 160, 108)
female_color = (236, 191, 255)


def faceBox(faceNet, frame):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [
                                 104, 117, 123], swapRB=False)
    faceNet.setInput(blob)
    detection = faceNet.forward()
    bboxs = []
    for i in range(detection.shape[2]):
        confidence = detection[0, 0, i, 2]
        if confidence > 0.7:
            x1 = int(detection[0, 0, i, 3]*frameWidth)
            y1 = int(detection[0, 0, i, 4]*frameHeight)
            x2 = int(detection[0, 0, i, 5]*frameWidth)
            y2 = int(detection[0, 0, i, 6]*frameHeight)
            bboxs.append([x1, y1, x2, y2])

    return frame, bboxs


faceProto = "weights/opencv_face_detector.pbtxt"
faceModel = "weights/opencv_face_detector_uint8.pb"

ageProto = "weights/age_deploy.prototxt"
ageModel = "weights/age_net.caffemodel"

genderProto = "weights/gender_deploy.prototxt"
genderModel = "weights/gender_net.caffemodel"

faceNet = cv2.dnn.readNet(faceModel, faceProto)
ageNet = cv2.dnn.readNet(ageModel, ageProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
ageList = ['(0-2)', '(4-6)', '(8-12)', '(13-17)', '(18, 24)',
           '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']

padding = 20


class FaceDetector(QThread):
    status = pyqtSignal(str)
    changePixmap = pyqtSignal(QImage)
    result = pyqtSignal(list)

    canDetect: bool = True
    canDraw: bool = False
    cameraIndex: int = 0

    drawFace: bool = False
    drawAge: bool = False
    drawGender: bool = False

    @pyqtSlot()
    def run(self) -> None:
        self.status.emit(f"CAM {str(self.cameraIndex)} Starting")
        try:
            cap = cv2.VideoCapture(self.cameraIndex)
            self.status.emit("Capturing")
            while cap.isOpened() and self.canDetect:
                _, frame = cap.read()

                data = []
                frame, bboxes = faceBox(faceNet, frame)
                for bbox in bboxes:
                    face = frame[
                        max(0, bbox[1]-padding):min(bbox[3]+padding, frame.shape[0]-1),
                        max(0, bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)
                    ]
                    blob = cv2.dnn.blobFromImage(
                        face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                    genderNet.setInput(blob)
                    genderPred = genderNet.forward()
                    gender = genderList[genderPred[0].argmax()]

                    ageNet.setInput(blob)
                    agePred = ageNet.forward()
                    age = ageList[agePred[0].argmax()]

                    data.append({
                        "cam": self.cameraIndex,
                        "age": age,
                        "gender": gender
                    })

                    if self.canDraw:
                        dcolor = box_color
                        if self.drawFace:
                            x1, y1, x2, y2 = bbox
                            cv2.rectangle(frame, (x1, y1),
                                          (x2, y2), dcolor, 2)

                        label = ""
                        gen_color = male_color if gender == "Male" else female_color
                        if self.drawAge:
                            dcolor = box_color
                            label += str(age)
                        if self.drawGender and self.drawAge:
                            label += " | "
                        if self.drawGender:
                            dcolor = gen_color
                            label += gender

                        if self.drawAge or self.drawGender:
                            cv2.rectangle(
                                frame, (bbox[0], bbox[1]-30), (bbox[2], bbox[1]), dcolor, -1)

                            cv2.putText(
                                frame, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

                self.result.emit(data)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                image = QImage(
                    frame,
                    w,
                    h,
                    bytes_per_line,
                    QImage.Format.Format_BGR888
                )
                self.changePixmap.emit(image)
            cap.release()
        except Exception as e:
            self.status.emit(str(e))
            print(str(e))

    def toggleDraw(self):
        self.canDraw = not self.canDraw

    def setDraw(self, a0: bool):
        if self.canDraw != a0:
            self.canDraw = a0

    def toggleDetect(self):
        self.canDetect = not self.canDetect

    def setDetect(self, a0: bool):
        if self.canDetect != a0:
            self.canDetect = a0
            if self.canDetect:
                self.status.emit(f"CAM {self.cameraIndex} starting")
            else:
                self.status.emit("Camera closed")

    def setCameraIndex(self, a0: int):
        self.cameraIndex = a0

    def setDrawOption(self, opt: str, a0: bool):
        if hasattr(self, opt):
            setattr(self, opt, a0)
