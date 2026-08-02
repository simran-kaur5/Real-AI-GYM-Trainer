from core.base_exercise import BaseExercise

class ShoulderPressDetector(BaseExercise):
    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160
    MIN_VISIBILITY = 0.7

    # indices of landmarks
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
            self.reps = 0
            self.stage = None

    def process(self,landmarks) -> dict:
    
            left_vis = landmarks[self.LEFT_ELBOW].visibility
            right_vis = landmarks[self.RIGHT_ELBOW].visibility
    
            if left_vis >= right_vis: # Use the arm with better landmark visibility
                hip_idx, knee_idx, elbow_idx, shoulder_idx,wrist_idx = self.LEFT_HIP , self.LEFT_KNEE,self.LEFT_ELBOW,self.LEFT_SHOULDER ,self.LEFT_WRIST# take best visibilty indices
            else:
                hip_idx, knee_idx,elbow_idx, shoulder_idx,wrist_idx = self.RIGHT_HIP , self.RIGHT_KNEE,self.RIGHT_ELBOW,self.RIGHT_SHOULDER,self.RIGHT_WRIST
    
            elbow_angle = self.calculate_angle(
                self.get_point(landmarks,shoulder_idx),
                self.get_point(landmarks,elbow_idx),
                self.get_point(landmarks,wrist_idx)
            )
    
            # check visibilty
            key_landmark_visibilty = landmarks[shoulder_idx].visibility >= self.MIN_VISIBILITY and landmarks[elbow_idx].visibility >= self.MIN_VISIBILITY and landmarks[wrist_idx].visibility >= self.MIN_VISIBILITY
    
            if key_landmark_visibilty:
                if elbow_angle < self.DOWN_THRESHOLD:
                    self.stage = "down"

                if elbow_angle > self.UP_THRESHOLD and self.stage == "down":
                    self.stage = "up"
                    self.reps += 1

            if elbow_angle>=self.UP_THRESHOLD:
                extension_status = "FULL EXTENSION"
            elif elbow_angle>=130:
                extension_status = "NEARLY EXTENDED"
            elif elbow_angle >= self.DOWN_THRESHOLD:
                extension_status = "PRESSING"
            else:
                extension_status = "START POSITION"

            back_angle = self.calculate_angle(
                self.get_point(landmarks,shoulder_idx),
                self.get_point(landmarks,hip_idx),
                self.get_point(landmarks,knee_idx)
            )    
                
    
            if back_angle>=160:
                back_arch_status = "Neutral"
            elif back_angle>=140:
                back_arch_status = "Slight Arch"
            else:
                back_arch_status = "Excessive Arch"
    
            return { 
                "reps":self.reps,
                "elbow_angle": int(elbow_angle),
                "extension_status":extension_status,
                "back_arch_status":(back_arch_status)
            }                   
    