import numpy
import cv2
import math
import mediapipe
import sound_server
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

def openCamera():
    vid = cv2.VideoCapture(0)
    if not (vid.isOpened()):
        print("Could not open video device")
        vid.release()
    return vid

def closeCamera(vid):
    if vid == None or not vid.isOpened():
        return
    vid.release()
    cv2.destroyAllWindows()

fingerTips = [
    handsModule.HandLandmark.THUMB_TIP,
    handsModule.HandLandmark.INDEX_FINGER_TIP,
    handsModule.HandLandmark.MIDDLE_FINGER_TIP,
    handsModule.HandLandmark.RING_FINGER_TIP,
    handsModule.HandLandmark.PINKY_TIP
]


# def get_freq(x_pos, freq_offset, freq_range, n_segments):
#     x_pos * 
 
def start_capture():
    capture = openCamera()
    frameWidth = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    frameHeight = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    ss = sound_server.SoundServer()
    ss.start()
    with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
    
        while (True):
    
            ret, frame = capture.read()
    
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            k = 0
            if results.multi_hand_landmarks != None:
                for handLandmarks in results.multi_hand_landmarks:
                    for point in fingerTips:
                        normalizedLandmark = handLandmarks.landmark[point]
                        if normalizedLandmark.y < 0.5:
                            sound_server.add_sound_async(ss,int(normalizedLandmark.x * 100 + 200))
                        pixelCoordinatesLandmark = drawingModule._normalized_to_pixel_coordinates(normalizedLandmark.x, normalizedLandmark.y, frameWidth, frameHeight)
    
                        cv2.circle(frame, pixelCoordinatesLandmark, 5, (11 * k, 255, 0), -1)
    
            cv2.imshow('Test hand', frame)
    
            if cv2.waitKey(1) == 27:
                break

    ss.stop_sound_server()

start_capture()