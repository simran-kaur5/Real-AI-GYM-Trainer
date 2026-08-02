from abc import ABC, abstractmethod
import math

class BaseExercise(ABC):
    def __init__(self):
        self.reps = 0
        self.stage = None # user position=>up,down

    def calculate_angle(self,a,b,c):
        ax, ay = a[0] - b[0] , a[1] - b[1]
        cx, cy = c[0] - b[0] , c[1] - b[1]

        dot = ax*cx + ay*cy # dot product=> tells how much two vectors in same direction

        mag_a = math.sqrt(ax**2 + ay**2) # calculate magnitude
        mag_c = math.sqrt(cx**2 + cy**2)

        if mag_a * mag_c ==0:
            return 0.0

        # dot product + magnitude gives => angle
        cos_angle = max(-1.0,min(1.0,dot / (mag_a * mag_c)))  # value must be in between -1 and 1

        return math.degrees(math.acos(cos_angle)) # converts to degrees




    def get_point(self,landmarks,idx):
        p = landmarks[idx]

        return (p.x,p.y)

    @abstractmethod
    def process(self,landmarks):
        pass

    @abstractmethod
    def reset(self):
        pass

