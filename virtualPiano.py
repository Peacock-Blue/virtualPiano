import cv2
import mediapipe
import sound


class VirtualPiano:

    def __init__(self):
        self.drawingModule = mediapipe.solutions.drawing_utils
        self.handsModule = mediapipe.solutions.hands
        self.fingerTips = [self.handsModule.HandLandmark.THUMB_TIP, self.handsModule.HandLandmark.INDEX_FINGER_TIP,
                           self.handsModule.HandLandmark.MIDDLE_FINGER_TIP,
                           self.handsModule.HandLandmark.RING_FINGER_TIP,
                           self.handsModule.HandLandmark.PINKY_TIP]
        self.camera = None
        self.soundServer = None

    def openCamera(self):
        self.camera = cv2.VideoCapture(0)
        if not (self.camera.isOpened()):
            print("Could not open video device")
            self.camera.release()

    def closeCamera(self):
        if self.camera is None or not self.camera.isOpened():
            return
        self.camera.release()
        cv2.destroyAllWindows()

    def openSound(self):
        self.soundServer = sound.SoundServer()
        self.soundServer.start()

    def closeSound(self):
        self.soundServer.stop_sound_server()

    def detectHand(self, image):
        width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        with self.handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7,
                                    max_num_hands=2) as hands:
            results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            k = 0
            if results.multi_hand_landmarks is not None:
                for handLandmarks in results.multi_hand_landmarks:
                    for point in self.fingerTips:
                        normalizedLandmark = handLandmarks.landmark[point]
                        if normalizedLandmark.y < 0.5:
                            return True, normalizedLandmark.x
                        landmark = self.drawingModule._normalized_to_pixel_coordinates(normalizedLandmark.x,
                                                                                       normalizedLandmark.y,
                                                                                       width, height)
                        cv2.circle(image, landmark, 5, (11 * k, 255, 0), -1)
        cv2.imshow('Test hand', image)
        return False, None

    def run(self):
        self.openCamera()
        self.openSound()
        while True:
            _, frame = self.camera.read()
            ret, x = self.detectHand(frame)
            if ret:
                sound.add_sound_async(self.soundServer, int(x * 100 + 200))
            if cv2.waitKey(1) == 27:
                break
        self.closeSound()
        self.closeCamera()
