from core.base_exercise import BaseExercise

class PushUpsDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7
    HIP_SAG_TOLERANCE = 0.08

    # indices of landmarks
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
            self.reps = 0
            self.stage = None

    def process(self,landmarks) -> dict:
    
            left_vis = landmarks[self.LEFT_ELBOW].visibility
            right_vis = landmarks[self.RIGHT_ELBOW].visibility
    
            if left_vis >= right_vis: # Use the arm with better landmark visibility
                hip_idx, ankle_idx, elbow_idx, shoulder_idx,wrist_idx = self.LEFT_HIP , self.LEFT_ANKLE,self.LEFT_ELBOW,self.LEFT_SHOULDER ,self.LEFT_WRIST# take best visibilty indices
            else:
                hip_idx, ankle_idx,elbow_idx, shoulder_idx,wrist_idx = self.RIGHT_HIP , self.RIGHT_ANKLE,self.RIGHT_ELBOW,self.RIGHT_SHOULDER,self.RIGHT_WRIST
    
            elbow_angle = self.calculate_angle(
                self.get_point(landmarks,shoulder_idx),
                self.get_point(landmarks,elbow_idx),
                self.get_point(landmarks,wrist_idx)
            )

            body_angle = self.calculate_angle(
                self.get_point(landmarks,shoulder_idx),
                self.get_point(landmarks,hip_idx),
                self.get_point(landmarks,ankle_idx)
            )
            #  took y because we want to handle top<-> down movements
            shoulder_y = landmarks[shoulder_idx].y
            ankle_y = landmarks[ankle_idx].y
            hip_y = landmarks[hip_idx].y

            expected_hip_y = (shoulder_y + ankle_y) /2
            hip_deviation = hip_y - expected_hip_y
    
            # check visibilty
            key_landmark_visibilty = landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
    
            if key_landmark_visibilty:
                if elbow_angle < self.DOWN_THRESHOLD:
                    self.stage = "down"

                if elbow_angle > self.UP_THRESHOLD and self.stage == "down":
                    self.stage = "up"
                    self.reps += 1

            if body_angle>=self.UP_THRESHOLD:
                body_alignment = "Straight"
            elif body_angle>140:
                body_alignment = "Slight Bend"
            else:
                body_alignment = "Poor Form"


            if abs(hip_deviation)<=self.HIP_SAG_TOLERANCE:
                hip_status = "LEVEL"
            elif hip_deviation > self.HIP_SAG_TOLERANCE:
                hip_status = "SAGGING"  # hip is more down
            else:
                hip_status = "PIKED UP"  # hip is up
    
            return { 
                "reps":self.reps,
                "elbow_angle": int(elbow_angle),
                "body_alignment":body_alignment,
                "hip_status":(hip_status)
            }                   
    