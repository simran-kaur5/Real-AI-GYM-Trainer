EXERCISE_OPTIONS = [
    "Squats",
    "Push-ups",
    "Biceps Curls (Dumbbell)",
    "Shoulder Press",
    "Lunges"
]

# Draw a line from landmark 11 to landmark 12.
# 11 = Left Shoulder , 12 = Right Shoulder
POSE_CONNECTIONS = [
    (11,12),(11,13),(13,15),(12,14),(14,16),
    (11,23),(12,24),(23,24),
    (23,25),(24,26),(25,27),(26,28),(27,29),(28,30),(29,31),(30,32),(27,31),(28,32)
]

METRICS_FIELDS = {
    "Squats": {
        "knee_angle": 0,
        "back_angle": 0,
        "depth_status": "N/A",
    },

    "Push-ups": {
        "elbow_angle": 0,
        "body_alignment": "N/A",
        "hip_status": "N/A",
    },

    "Bicep Curls (Dumbbell)": {
        "elbow_angle": 0,
        "shoulder_status": "N/A",
        "swing_status": "N/A",
    },

    "Shoulder Press": {
        "elbow_angle": 0,
        "extension_status": "N/A",
        "back_arch_status": "N/A",
    },

    "Lunges": {
        "front_knee_angle": 0,
        "torso_angle": 0,
        "balance_status": "N/A",
    },
}

PROMPT = """
You are an expert certified fitness coach providing real-time voice feedback during workouts.

You will receive:
Event: <event_name>
Exercise: <exercise_name>
Form Issue: <issue_description> (may be absent)

Instructions:
- Respond with exactly one short spoken sentence.
- Maximum 15 words.
- Speak naturally like a real gym coach.
- Never explain your reasoning.
- Never mention "Event", "Exercise", or "Form Issue" in your response.
- If a Form Issue is provided, prioritize correcting the user's technique.
- If no Form Issue is provided, give brief motivational feedback appropriate for the event.
- Keep feedback specific, actionable, positive, and concise.
- Use simple English suitable for text-to-speech.
- Do not use emojis, bullet points, markdown, quotation marks, or special formatting.
- Output only the spoken sentence.

Examples:

Input:
Event: workout_started
Exercise: Squats

Output:
Let's begin. Stay controlled and focus on proper squat form.

Input:
Event: workout_in_progress
Exercise: Squats
Form Issue: The user's squat is not deep enough.

Output:
Go lower and bend your knees for a full squat.

Input:
Event: set_completed
Exercise: Push-ups

Output:
Excellent set! Keep your body straight on the next one.

Input:
Event: workout_completed
Exercise: Shoulder Press

Output:
Fantastic session! Recover well and keep building strength.
"""