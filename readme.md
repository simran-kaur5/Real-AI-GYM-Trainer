# Real AI Gym Trainer

Real AI Gym Trainer is a computer vision–based fitness coach that helps users perform exercises with proper form. It uses a webcam and MediaPipe Pose to detect body landmarks in real time, count repetitions, track sets, and provide instant feedback during workouts.

Along with exercise tracking, the application includes an AI fitness assistant powered by Groq to answer workout-related questions and guide users throughout their fitness journey.

## Features

* Real-time pose estimation using MediaPipe
* Automatic repetition and set counting
* Exercise-specific form analysis
* Live workout metrics
* Workout history tracking
* AI fitness assistant for workout guidance
* Voice responses for a more interactive experience
* Responsive landing page

## Built With

* Python
* Streamlit
* MediaPipe
* OpenCV
* NumPy
* SQLite
* Groq API
* HTML
* CSS


## Getting Started

Clone the repository:

```bash
git clone https://github.com/simran-kaur5/Real-AI-GYM-Trainer.git
```

Move into the project folder:

```bash
cd Real-AI-GYM-Trainer
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Groq API key:

```env
GROQ_API_KEY=your_api_key
```

Run the application:

```bash
streamlit run main.py
```

## Live Demo

**Landing Page:** *(https://reliable-meerkat-8df671.netlify.app/)*

**Application:** *(https://real-ai-gym-trainer.streamlit.app/)*

## Future Improvements

* Support more exercises
* User authentication
* Cloud database integration
* Personalized workout plans
* Mobile-friendly version
* Performance analytics

## About

I built this project to explore how computer vision and AI can be combined to create a practical fitness application. The project uses MediaPipe for real-time pose estimation, Streamlit for the user interface, and Groq to provide an AI-powered fitness assistant. It was a great opportunity to work with real-time video processing, WebRTC, and AI integration while building something that solves a real-world problem.

## License

This project is available for learning and portfolio purposes.
