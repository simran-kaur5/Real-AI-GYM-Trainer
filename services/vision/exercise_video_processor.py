import threading
import os
import cv2
import av
import numpy as np
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from detectors.squat import SquatDetector
from detectors.biceps_curls import BicepsCurlsDetector
from detectors.lunges import LungesDetector 
from detectors.pushup import PushUpsDetector
from detectors.shoulder_press import ShoulderPressDetector
from services.config.workout_config import POSE_CONNECTIONS

class VideoProcessorClass(VideoProcessorBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_metrics = None
        self._exercise_type = "Squats"

        model_path = os.path.join(os.getcwd(),"ml_models","pose_landmarker_full.task")
        base_option = python.BaseOptions(model_asset_path=model_path)  # load this model

        options = vision.PoseLandmarkerOptions(  # creates setting for detecting
            base_options = base_option,
            running_mode = vision.RunningMode.VIDEO,
            min_pose_detection_confidence = 0.7, # accept only the frame
            min_pose_presence_confidence = 0.7,
            min_tracking_confidence = 0.7,
            output_segmentation_masks = False
        )

        self._landmarker = vision.PoseLandmarker.create_from_options(options) # AI Detector

        self._detectors = {
            "Squats":SquatDetector(),
            "Push-ups":PushUpsDetector(),
            "Bicep Curls (Dumbbell)":BicepsCurlsDetector(),
            "Shoulder Press":ShoulderPressDetector(),
            "Lunges":LungesDetector()
        }



        self._frame_timestamps_ms = 0

    def set_latest_metrics(self,metrics):
        with self._lock:
            print("SET instance:", id(self))
            self._latest_metrics = metrics.copy()

    def get_latest_metrics(self):
        print("GET instance:", id(self))
        with self._lock:
            print("GET metrics:", self._latest_metrics)
            return None if self._latest_metrics is None else self._latest_metrics.copy()

    def set_exercise(self,exercise_type):
        with self._lock:
            self._exercise_type = exercise_type

    def get_execise(self):
        with self._lock:
            return self._exercise_type

    def _draw_skeleton(self,img,landmarks):
        h, w = img.shape[:2]  # dimensions of img can be 480*648 (h*w)

        for start_idx,end_idx in POSE_CONNECTIONS:
            p1 = landmarks[start_idx]
            p2 = landmarks[end_idx]

            if p1.visibility > 0.7 and p2.visibility > 0.7: # if the part of body is visible then draw line
                cv2.line(
                    img,
                    (int(p1.x * w), int(p1.y*h)),
                    (int(p2.x * w),int(p2.y*h)),
                    (0,255,0), # skelton will be of green color
                    8 # line thickness
                )

        for lm in landmarks:
            if lm.visibility > 0.7:
                cv2.circle(
                    img,
                    (int(lm.x*w),int(lm.y * h)),
                    8,
                    (255, 0, 0),
                    -1 # thickness
                )

        return img  # modified img

    # If MediaPipe cannot detect a person, display warning messages on the screen.
    def _draw_no_pose_warning(self,img):
        cv2.putText(
            img,
            "NO POSE DETECTED",
            (30,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, #font scale
            (0,255,0), # font color
            2, # thickness
            cv2.LINE_AA # controls how the text edges are drawn.
        )

        cv2.putText(
            img,
            "PLEASE FACE THE CAMERA",
            (30,100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2,
            cv2.LINE_AA
        )

    def _draw_overlays(self, img, metrics, ex_type):
        if ex_type == "Squats":
            self._draw_squats_overlays(img, metrics)
        elif ex_type =="Push-ups":
            self._draw_pushup_overlays(img, metrics)
        elif ex_type =="Bicep Curls (Dumbbell)":
            self._draw_curl_overlays(img, metrics) 
        elif ex_type =="Shoulder Press":
            self._draw_press_overlays(img, metrics)  
        elif ex_type =="Lunges":
            self._draw_lunges_overlays(img, metrics) 

    def _draw_squats_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"DEPTH: {metrics['depth_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    def _draw_pushup_overlays(self, img, metrics):
        h, _ = img.shape[:2]

        cv2.putText(
            img,
            f"BODY: {metrics['body_alignment']} | HIP: {metrics['hip_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    def _draw_curl_overlays(self, img, metrics):
        h, _ = img.shape[:2]
    
        cv2.putText(
            img,
            f"SWING: {metrics['swing_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    def _draw_press_overlays(self, img, metrics):
        h, _ = img.shape[:2]
    
        cv2.putText(
            img,
            f"EXT: {metrics['extension_status']} | BACK: {metrics['back_arch_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    def _draw_lunges_overlays(self, img, metrics):
        h, _ = img.shape[:2]
    
        cv2.putText(
            img,
            f"BALANCE: {metrics['balance_status']}",
            (20,h-20),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

    def recv(self,frame): # this called automatically whenever frame arrives 
        image = np.asarray(
            cv2.flip(frame.to_ndarray(format="bgr24"),1),
            dtype=np.uint8 # each image pixel between 0- 255 2^8 -1
        )

        mp_image = mp.Image(
            image_format = mp.ImageFormat.SRGB,
            data = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
        )

        self._frame_timestamps_ms += 30
        result = self._landmarker.detect_for_video(mp_image, self._frame_timestamps_ms)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks[0]

            self._draw_skeleton(image,landmarks)

            ex_type = self.get_execise()

            detector = self._detectors.get(ex_type)

            if detector:
                
                metrics = detector.process(landmarks)

                self._draw_overlays(image, metrics, ex_type)

                self.set_latest_metrics(metrics)
        else:
            self._draw_no_pose_warning(image)

            with self._lock:
                if self._latest_metrics is not None:
                    self._latest_metrics["pose_detected"] = False
                else:
                    self._latest_metrics = {"pose_detected":False}

        return av.VideoFrame.from_ndarray(image,format="bgr24")
