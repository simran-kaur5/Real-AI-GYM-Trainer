import time
import streamlit as st

class VoicePipeline:
    def __init__(self,llm,tts):
        self.llm =llm
        self.tts = tts
        self.last_spoken_at =0

    def _find_form_issue(self,exercise,metrics):
        print("Checking issue for:", exercise)
        print("Metrics received:", metrics)
        if "issue" in metrics:
            return metrics["issue"] # if detector itself found a issue

        if exercise == "Squats":
            depth = metrics.get("depth_status","")

            back_angle = metrics.get("back_angle",180)

            if depth == "TOO HIGH":
                return "The user's squat is not deep enough - knees are not bending sufficiently"

            if back_angle < 130:
                return "The user is leaning too far forward during the squat."

            
        elif exercise == "Push-ups":
            alignment = metrics.get("body_alignment","")
            hip_status = metrics.get("hip_status","")

            if alignment == "Poor Form":
               return "The user's body is not straight during the push-ups."

            if hip_status == "SAGGING":
                return "The user's hips are sagging down during the push-ups."

            if hip_status == "PIKED UP":
                return "The user's hips are too high - lower them to form a straight line."
            

        elif exercise == "Biceps Curls (Dumbbell)":
            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")
            
            if swing == "SWINGING":
                return "The user is swinging their torso during the curl — keep the body still."

            if shoulder == "ELBOW DRIFTING":
                return "The user's elbow is drifting away from their side during the curl."
  

        elif exercise == "Shoulder Press":
            extension_status = metrics.get("extension_status", "")
            back_arch_status = metrics.get("back_arch_status", "")

            if extension_status in ["NEARLY EXTENDED", "PRESSING"]:
                return "Fully extend your arms overhead. Do not stop halfway."

            if back_arch_status == "Slight Arch":
                return "Keep your core tight and avoid arching your lower back."

            if back_arch_status == "Excessive Arch":
                return "Your lower back is arching too much. Engage your core and keep a neutral spine."
            

        elif exercise == "Lunges":
            balance_status = metrics.get("balance_status", "")

            if balance_status == "OFF BALANCED":
                return "The user is losing balance during the lunge. Keep the torso upright and distribute weight evenly."

        return None           


    def process_event(self,event,exercise,metrics):
        print("Event received:", event)
        issue = self._find_form_issue(exercise,metrics)
        

        now = time.time()

        is_major_issue = event in ["workout_started","set_completed","workout_completed"] # checks whether the event is important

        if not is_major_issue:
            if not issue:
                return None

            if now - self.last_spoken_at < 5:
                return None

        print("process_event called")
        print("Event:", event)
        print("Exercise:", exercise)
        print("Metrics:", metrics)


        text = self.llm.give_feedback(event,issue) 
        voice = self.tts.speech(text)

        self.last_spoken_at = now

        return voice , text


def autoplay_audio(audio_bytes):
    if not audio_bytes:
        return

    st.markdown("<style>[data-testid='stAudio'] {diplay: none;}</style>",unsafe_allow_html=True)
    st.audio(audio_bytes,format="audio/mp3",autoplay=True)