import streamlit as st
import time
import os
import pandas as pd
from services.auth.login_wall import render_login_wall
from services.state.session_default import initial_session_default
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css,inject_local_font
from services.persistance.exercise_repository import _init_db
from streamlit_webrtc import webrtc_streamer,WebRtcMode
from services.tracking.metrics import sync_metrics_update
from services.persistance.exercise_repository import get_users_exercise
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio
from dotenv import load_dotenv

def main():
    st.set_page_config(
    page_icon = "🏋️",
    page_title = "AI Real-time GYM Coach",
    initial_sidebar_state = "expanded", # sidebar remains open
    layout = "centered"
    )

    load_css(os.path.join(os.getcwd(),"static","style.css"))
    inject_local_font(os.path.join(os.getcwd(),"static","AdobeClean.otf"),"AdobeClean")

    _init_db()

    if not render_login_wall():
        return 

    initial_session_default()

    if "voice_pipeline" not in st.session_state:
        try:
            load_dotenv()
            api_key = os.environ.get("GROQ_API_KEY","")

            if not api_key and hasattr(st,"secrets") and "GROQ_API_KEY" in st.secrets:
                api_key = st.secrets["GROQ_API_KEY"]

            groq_client = Groq(api_key=api_key) # obj that communicates with Groq's server
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()

            st.session_state.voice_pipeline = VoicePipeline(llm_coach,tts)

        except Exception as e:
            st.session_state.voice_pipeline = None


    workout_started = st.session_state.get("workout_started",False)

    with st.sidebar:
        st.title("AI Coach")

        if st.session_state.username:
            st.caption(f"Login as {st.session_state.username}")

        st.divider()

        st.subheader("Workout Plan")

        if not workout_started:
            plan_exercise = st.selectbox("Exercise",options=EXERCISE_OPTIONS,key="plan_exercise")

            plan_sets = st.number_input("Sets",min_value=0,max_value=50,step=1,key="plan_sets")
            plan_reps = st.number_input("Reps per Set",min_value=0,max_value=50,step=1,key="plan_reps")

            st.markdown("")

            start_session_button = st.button("Start Session",width="stretch",key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise = plan_exercise,
                        metrics={} # workout has just started
                    )

                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_completed = False
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets") # student decided for how many sets
            reps = st.session_state.get("reps_per_set")

            st.info(f"**{exercise}** -- {sets} Sets / {reps} Reps")

            end_session_button = st.button("End workout",key = "end_session_button",width="stretch")

            if end_session_button:
                st.session_state.workout_started = False

                if st.session_state.voice_pipeline:
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics= {}
                    )

                    if result:
                        st.session_state.audio_to_play,st.session_state.coach_feedback = result


                st.rerun()


        # show progress while workout
        if workout_started:
            st.divider()

            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps")
            current_set_reps = st.session_state.get("current_set_reps")
            reps_per_set = st.session_state.get("reps_per_set")
            sets_completed = st.session_state.get("sets_completed")
            target_sets = st.session_state.get("target_sets")

            st.subheader("Progress")

            row1_col1, row1_col2 = st.columns([3, 1])

            with row1_col1:
                st.write("**Total Reps**")
            with row1_col2:
                st.write(f"**{total_reps}**")

            row2_col1, row2_col2 = st.columns([3, 1])

            with row2_col1:
                st.write("**Current Set Reps**")
            with row2_col2:
                st.write(f"**{current_set_reps}/{reps_per_set}**")

            row3_col1, row3_col2 = st.columns([3, 1])

            with row3_col1:
                st.write("**Sets Completed**")
            with row3_col2:
                st.write(f"**{sets_completed}/{target_sets}**")

            st.divider()

            if exercise == "Squats":
                st.subheader("Squat Metrics")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Knee Angle**")
                with col2:
                    st.write(f"**{st.session_state.knee_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Back Angle**")
                with col2:
                    st.write(f"**{st.session_state.back_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Depth Status**")
                with col2:
                    st.write(f"**{st.session_state.depth_status}**")


            elif exercise == "Push-ups":
                st.subheader("Push-up Metrics")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Elbow Angle**")
                with col2:
                    st.write(f"**{st.session_state.elbow_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Body Alignment**")
                with col2:
                    st.write(f"**{st.session_state.body_alignment}**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Hip Position**")
                with col2:
                    st.write(f"**{st.session_state.hip_status}**")


            elif exercise == "Biceps Curls (Dumbbell)":
                st.subheader("Biceps Curl Metrics")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Elbow Angle**")
                with col2:
                    st.write(f"**{st.session_state.elbow_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Shoulder Stability**")
                with col2:
                    st.write(f"**{st.session_state.shoulder_status}**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Swing Detection**")
                with col2:
                    st.write(f"**{st.session_state.swing_status}**")


            elif exercise == "Shoulder Press":
                st.subheader("Shoulder Press Metrics")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Elbow Angle**")
                with col2:
                    st.write(f"**{st.session_state.elbow_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Arm Extension**")
                with col2:
                    st.write(f"**{st.session_state.extension_status}**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Back Arch**")
                with col2:
                    st.write(f"**{st.session_state.back_arch_status}**")


            elif exercise == "Lunges":
                st.subheader("Lunge Metrics")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Front Knee Angle**")
                with col2:
                    st.write(f"**{st.session_state.front_knee_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Torso Angle**")
                with col2:
                    st.write(f"**{st.session_state.torso_angle}°**")

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write("**Balance Status**")
                with col2:
                    st.write(f"**{st.session_state.balance_status}**")


    st.title("AI Real-time GYM Coach")
    st.markdown("#### Real-time pose detection with proactive AI voice coaching")

    if st.session_state.get("audio_to_play"):
        autoplay_audio(st.session_state.audio_to_play)

    if st.session_state.get("coach_feedback"):
        st.markdown("")
        st.success(f" **Coach** {st.session_state.coach_feedback}")

    if not workout_started:
        st.markdown(
            f"""
            <div style="
                border: 10px dashed #444;
                border-radius: 0px;
                padding: 48px 32px;
                text-align: center;
                color:#888;
                margin-top: 32px;
                ">
                <h2 style = "color:#ccc; margin-bottom:8px;"> Set your workout plan</h2>
                <p style = "font-size:1.05rem;">
                    Choose your exercise, sets and reps in the sidebar,<br>
                    then click <strong>Start Workout</strong> to activate the camera and AI coach
                </p>
            </div>
        """,unsafe_allow_html=True)
    else:

        from services.vision.exercise_video_processor import VideoProcessorClass

        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDONLY,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302",
                            "stun:stun1.l.google.com:19302"
                        ]
                    }
                ]
            },
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(1)
            st.rerun()

    st.divider()

    st.markdown("#### Workout History")

    user_id = st.session_state.get("user_id",0)

    if isinstance(user_id,int):
        history_rows = get_users_exercise(user_id)

        arr = [
            {
                "Exercise" : row["exercise_name"],
                "Reps": row["reps"],
                "Sets": row["sets"],
                "Time (sec)": row["time"],
                "Date": row["created_at"]
            }
            for row in history_rows
        ]

        df = pd.DataFrame(arr)

        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date  # only date
            agg_df = df.groupby(["Exercise","Date"]).agg({
                "Reps":"sum",
                "Sets":"sum",
                "Time (sec)": "sum"
            }).reset_index()
            agg_df.index+=1
            st.table(df,border="horizontal")
        else:
            st.info("No workout history found.")



if __name__ == "__main__":
    main()