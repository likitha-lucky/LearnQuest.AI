import os
import json
import re
import base64
import time
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="LearnQuest AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception:
        client = None


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "page": "home",

    "board": "",
    "class_level": "",
    "subject": "",
    "topic": "",

    "explanation": "",
    "summary": "",
    "example": "",

    "student_question": "",
    "student_answer": "",
    "student_answer_error": "",
    "answer_summary": "",
    "learning_mode": "",
    "voice_audio": None,
    "generated_visual": None,
    "generated_video": None,
    "topic_learning_mode": "",
    "topic_voice_audio": None,
    "topic_summary": "",
    "topic_visual": None,
    "topic_video": None,

    "gemini_error": "",

    "quiz_questions": [],
    "challenge_questions": [],

    "mission": 1,

    "quiz_index": 0,
    "challenge_index": 0,

    "quiz_score": 0,
    "challenge_score": 0,

    "xp": 0,

    "quiz_answered": False,
    "challenge_answered": False,

    "quiz_feedback": "",
    "challenge_feedback": "",

    "quest_complete": False,

    "result_celebrated": False,

    "lesson_generated": False,
    "quiz_generated": False,
    "challenge_generated": False,
}


for key, value in DEFAULT_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# SUBJECTS
# =========================================================

PRIMARY_SUBJECTS = [
    "Mathematics",
    "English",
    "Environmental Studies",
    "Science",
    "Social Studies",
    "Computer",
    "Languages"
]

MIDDLE_SUBJECTS = [
    "Mathematics",
    "Science",
    "Social Science",
    "English",
    "Computer Science",
    "Languages"
]

HIGHER_SUBJECTS = [
    "Physics",
    "Chemistry",
    "Mathematics",
    "Biology",
    "Computer Science",
    "English",
    "Accountancy",
    "Business Studies",
    "Economics",
    "History",
    "Political Science",
    "Geography",
    "Sociology",
    "Languages"
]


# =========================================================
# BACKGROUND
# =========================================================

def get_background_name(class_number):

    # Class 1-4  -> Space theme
    # Class 5-7  -> Superman theme
    # Class 8-10 -> Pixel theme
    # Class 11-12 -> Higher theme

    if class_number <= 4:

        return "space"

    elif class_number <= 7:

        return "superman"

    elif class_number <= 10:

        return "pixel"

    else:

        return "higher"


def find_background():

    class_value = st.session_state.get(
        "class_level",
        ""
    )

    if not class_value:

        return None

    try:

        class_number = int(class_value)

    except Exception:

        return None

    background_name = get_background_name(
        class_number
    )

    app_folder = Path(__file__).resolve().parent
    background_folder = app_folder / "assets" / "backgrounds"

    possible_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    for extension in possible_extensions:

        image_path = (
            background_folder
            / f"{background_name}{extension}"
        )

        if image_path.exists():

            return image_path

    return None


def apply_background():

    image_path = find_background()

    if image_path is None:

        st.markdown(
            """
            <style>

            .stApp {
                background:
                    linear-gradient(
                        135deg,
                        #eef5ff 0%,
                        #f8f4ff 50%,
                        #eefcf7 100%
                    );
            }

            </style>
            """,
            unsafe_allow_html=True
        )

        return

    try:

        image_bytes = image_path.read_bytes()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode()

        suffix = image_path.suffix.lower()

        if suffix in [".jpg", ".jpeg"]:

            mime = "image/jpeg"

        elif suffix == ".webp":

            mime = "image/webp"

        else:

            mime = "image/png"

        background_url = (
            f"data:{mime};base64,{encoded_image}"
        )

        st.markdown(
            f"""
            <style>

            .stApp {{
                background-image:
                    linear-gradient(
                        rgba(255,255,255,0.08),
                        rgba(255,255,255,0.08)
                    ),
                    url("{background_url}");

                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}

            </style>
            """,
            unsafe_allow_html=True
        )

    except Exception:

        pass


apply_background()


# =========================================================
# GENERAL CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------------------------------------------------------
       LEARNQUEST GLOBAL STYLE
       HTML here is ONLY styling. All visible interface content
       is still created with native Streamlit components.
       --------------------------------------------------------- */

    .block-container {
        max-width: 1100px;
        padding: 2rem 2.2rem 3rem 2.2rem;
        margin-top: 1.2rem;
        margin-bottom: 2rem;
        background: rgba(255,255,255,0.86) !important;
        border: 3px solid rgba(255,255,255,0.98);
        border-radius: 28px;
        box-shadow: 0 12px 40px rgba(50,60,100,0.14);
    }

    .stMarkdown, .stText, .stCaption, .stAlert {
        color: #173b67;
    }

    /* Strong white cards behind text on every learning page. */
    /* ---------------------------------------------------------
       SOFT PASTEL TEXT BOXES — ALL PAGES
       Home, Setup, Academy, Mission 1, Mission 2, Mission 3
       and Quest Complete all use gentle pastel cards.
       --------------------------------------------------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        background: linear-gradient(135deg, #fffdf7, #f8f4ff) !important;
        background-color: #fffdf7 !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
        border: 2px solid #eee4f7 !important;
        box-shadow: 0 8px 28px rgba(120,100,150,0.12) !important;
        overflow: hidden;
        animation: cardAppear 0.55s ease both;
    }

    /* Inner areas stay softly pastel instead of turning bright white. */
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stVerticalBlockBorderWrapper"] > div > div,
    div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, #fffdf7, #fbf8ff) !important;
        background-color: #fffdf7 !important;
        border-radius: 17px;
    }

    /* Gentle alternating pastel shades make different text boxes feel lively. */
    div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4n+1) {
        background: linear-gradient(135deg, #fff9df, #fffdf3) !important;
        border-color: #f3e6b3 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4n+2) {
        background: linear-gradient(135deg, #f2fbff, #f7f3ff) !important;
        border-color: #dce8f4 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4n+3) {
        background: linear-gradient(135deg, #fff1f7, #fff8fb) !important;
        border-color: #f2dce8 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:nth-of-type(4n+4) {
        background: linear-gradient(135deg, #effbf4, #f7fff9) !important;
        border-color: #d8eddf !important;
    }

    /* Keep inner content matched with each soft card. */
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] label,
    div[data-testid="stVerticalBlockBorderWrapper"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        color: #4d496b !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] label,
    div[data-testid="stVerticalBlockBorderWrapper"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        color: #173b67 !important;
    }

    /* Soft, friendly buttons. */
    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 14px;
        font-weight: 700;
        color: #173b67 !important;
        background: linear-gradient(135deg, #e9f2ff, #f2eaff) !important;
        border: 1px solid #cddcf4 !important;
        box-shadow: 0 4px 14px rgba(80,100,150,0.10);
        transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
    }

    .stButton > button[kind="primary"] {
        color: #ffffff !important;
        background: linear-gradient(135deg, #6fa8ff, #9a7bff) !important;
        border: 1px solid rgba(111,168,255,0.35) !important;
        box-shadow: 0 7px 20px rgba(111,130,220,0.22);
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 10px 24px rgba(80,100,150,0.18);
        filter: brightness(1.03);
    }

    .stButton > button:active {
        transform: scale(0.98);
    }

    /* Inputs */
    input, textarea {
        border-radius: 12px !important;
    }

    div[data-testid="stProgressBar"] {
        border-radius: 20px;
    }

    img {
        border-radius: 16px;
    }

    /* Result-state animations. */
    div[data-testid="stAlert"] {
        border-radius: 18px !important;
    }

    div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {
        animation: badPulse 1.8s ease-in-out infinite;
    }

    div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {
        animation: softPulse 2.8s ease-in-out infinite;
    }

    div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {
        animation: heartPulse 1.7s ease-in-out infinite;
    }

    @keyframes cardAppear {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes softGradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes titleFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    @keyframes badPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(220, 70, 70, 0.08); }
        50% { box-shadow: 0 0 0 9px rgba(220, 70, 70, 0.10); }
    }

    @keyframes softPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.012); }
    }

    @keyframes heartPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 90, 150, 0.10); }
        50% { transform: scale(1.018); box-shadow: 0 0 0 10px rgba(230, 90, 150, 0.08); }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


def apply_page_theme(page):
    """Soft yellow animated theme for Home and Setup pages."""

    if page in ("home", "setup"):

        st.markdown(
            """
            <style>

            /* =====================================================
               SOFT YELLOW BACKGROUND — HOME + SETUP ONLY
               ===================================================== */

            .stApp {
                background:
                    radial-gradient(circle at 8% 15%, rgba(255,255,255,0.96) 0 7%, transparent 24%),
                    radial-gradient(circle at 92% 18%, rgba(255,239,170,0.78) 0 8%, transparent 27%),
                    radial-gradient(circle at 15% 88%, rgba(255,246,198,0.90) 0 9%, transparent 28%),
                    radial-gradient(circle at 86% 82%, rgba(255,255,230,0.92) 0 8%, transparent 25%),
                    linear-gradient(135deg, #fffdf0, #fff8d9, #fffef4, #fff3c2);
                background-size: 160% 160%;
                animation: softYellowGradient 18s ease-in-out infinite;
                overflow-x: hidden;
            }

            /* White readable application card */
            .block-container {
                background: rgba(255,255,255,0.90) !important;
                border-color: rgba(255,255,255,0.98) !important;
                box-shadow: 0 18px 55px rgba(160,135,55,0.13) !important;
            }

            .block-container > div:first-child h1 {
                animation: titleFloat 3.5s ease-in-out infinite;
            }

            /* =====================================================
               INDEPENDENT FLOATING PANDA DECORATIONS
               Each panda has a different position, speed and path.
               They do NOT move together in a row.
               ===================================================== */

            .stApp::before {
                content: "🐼";
                position: fixed;
                left: 8vw;
                top: 78vh;
                z-index: 0;
                font-size: 24px;
                opacity: 0.55;
                pointer-events: none;
                animation: pandaFloatOne 11s ease-in-out infinite;
            }

            .stApp::after {
                content: "🐼";
                position: fixed;
                right: 10vw;
                top: 25vh;
                z-index: 0;
                font-size: 21px;
                opacity: 0.48;
                pointer-events: none;
                animation: pandaFloatTwo 14s ease-in-out infinite;
            }

            .main::before {
                content: "🐼";
                position: fixed;
                left: 32vw;
                top: 52vh;
                z-index: 0;
                font-size: 19px;
                opacity: 0.42;
                pointer-events: none;
                animation: pandaFloatThree 13s ease-in-out infinite;
            }

            .main::after {
                content: "🐼";
                position: fixed;
                right: 34vw;
                top: 72vh;
                z-index: 0;
                font-size: 23px;
                opacity: 0.45;
                pointer-events: none;
                animation: pandaFloatFour 16s ease-in-out infinite;
            }

            /* Soft background movement */
            @keyframes softYellowGradient {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            /* Panda 1: low → up → sideways → back down */
            @keyframes pandaFloatOne {
                0% {
                    transform: translate(0px, 30px) rotate(-5deg);
                }
                20% {
                    transform: translate(55px, -90px) rotate(6deg);
                }
                45% {
                    transform: translate(-25px, -210px) rotate(-7deg);
                }
                70% {
                    transform: translate(80px, -120px) rotate(5deg);
                }
                100% {
                    transform: translate(-10px, 25px) rotate(-4deg);
                }
            }

            /* Panda 2: different direction and timing */
            @keyframes pandaFloatTwo {
                0% {
                    transform: translate(0px, 0px) rotate(4deg);
                }
                25% {
                    transform: translate(-70px, 100px) rotate(-7deg);
                }
                50% {
                    transform: translate(35px, 220px) rotate(8deg);
                }
                75% {
                    transform: translate(-60px, 80px) rotate(-5deg);
                }
                100% {
                    transform: translate(10px, -20px) rotate(4deg);
                }
            }

            /* Panda 3: smaller, gentle floating path */
            @keyframes pandaFloatThree {
                0% {
                    transform: translate(-20px, 30px) scale(0.90);
                }
                30% {
                    transform: translate(90px, -70px) scale(1.08);
                }
                60% {
                    transform: translate(-60px, -190px) scale(0.95);
                }
                100% {
                    transform: translate(20px, 30px) scale(0.90);
                }
            }

            /* Panda 4: another independent path */
            @keyframes pandaFloatFour {
                0% {
                    transform: translate(15px, -10px) rotate(0deg);
                }
                25% {
                    transform: translate(-90px, 90px) rotate(8deg);
                }
                55% {
                    transform: translate(45px, 200px) rotate(-9deg);
                }
                80% {
                    transform: translate(100px, 60px) rotate(5deg);
                }
                100% {
                    transform: translate(15px, -10px) rotate(0deg);
                }
            }

            @media (prefers-reduced-motion: reduce) {
                .stApp::before,
                .stApp::after,
                .main::before,
                .main::after {
                    animation: none !important;
                }
            }

            </style>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(prompt):

    if client is None:

        return (
            None,
            "GEMINI_API_KEY was not found or "
            "Gemini client could not be created. "
            "Please check your .env file."
        )

    # IMPORTANT:
    # gemini-2.0-flash has been completely removed.
    # Do NOT add it back.

    models = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ]

    errors = []

    for model in models:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                return (
                    response.text.strip(),
                    ""
                )

        except Exception as error:

            errors.append(
                f"{model}: {str(error)}"
            )

    return (
        None,
        "\n\n".join(errors)
    )


# =========================================================
# GENERATE MISSION 1
# =========================================================

def generate_learning_content():

    board = st.session_state.board
    class_level = st.session_state.class_level
    subject = st.session_state.subject
    topic = st.session_state.topic

    prompt = f"""
You are a friendly school teacher and AI tutor.

Board: {board}
Class: {class_level}
Subject: {subject}
Topic: {topic}

Teach this topic in very simple language
suitable for this student's class.

Explain:

1. What the topic means
2. How it works
3. Important points
4. One easy example
5. A short revision summary

Do not use unnecessarily advanced terminology.

Return exactly in this format:

EXPLANATION:
Write a clear explanation using simple paragraphs.

SUMMARY:
Write 3 to 5 short revision points.

EXAMPLE:
Give one simple example.
"""

    answer, error = ask_gemini(prompt)

    if answer:

        explanation_match = re.search(
            r"EXPLANATION:\s*(.*?)(?=\nSUMMARY:)",
            answer,
            re.S | re.I
        )

        summary_match = re.search(
            r"SUMMARY:\s*(.*?)(?=\nEXAMPLE:)",
            answer,
            re.S | re.I
        )

        example_match = re.search(
            r"EXAMPLE:\s*(.*)",
            answer,
            re.S | re.I
        )

        st.session_state.explanation = (
            explanation_match.group(1).strip()
            if explanation_match
            else answer
        )

        st.session_state.summary = (
            summary_match.group(1).strip()
            if summary_match
            else ""
        )

        st.session_state.example = (
            example_match.group(1).strip()
            if example_match
            else ""
        )

        st.session_state.gemini_error = ""

        st.session_state.lesson_generated = True

        return True

    st.session_state.gemini_error = error

    st.session_state.lesson_generated = False

    return False


# =========================================================
# AI TUTOR
# =========================================================

def ask_ai_tutor(question):

    prompt = f"""
You are a friendly AI tutor.

Student class:
{st.session_state.class_level}

Subject:
{st.session_state.subject}

Main topic:
{st.session_state.topic}

Student question:
{question}

Answer the student's question clearly and simply.

Requirements:

- Use easy language.
- Explain step by step.
- Give an example if useful.
- Stay related to the topic.
- Do not make the answer unnecessarily advanced.
"""

    answer, error = ask_gemini(prompt)

    if answer:

        st.session_state.student_answer = answer

        st.session_state.student_answer_error = ""

        return True

    st.session_state.student_answer = ""

    st.session_state.student_answer_error = error

    return False



# =========================================================
# QUESTION LEARNING OPTIONS
# =========================================================

def generate_answer_summary():

    prompt = f"""
Create a short and easy summary of this AI tutor answer.

Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Student question:
{st.session_state.student_question}

AI tutor answer:
{st.session_state.student_answer}

Requirements:
- Use very simple student-friendly language.
- Give 3 to 5 short bullet points.
- Keep only the important ideas.
- Do not add unrelated information.
"""

    answer, error = ask_gemini(prompt)

    if answer:
        st.session_state.answer_summary = answer
        st.session_state.gemini_error = ""
        return True

    st.session_state.gemini_error = error
    return False


def generate_voice_for_answer():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available."
        return False

    text_to_speak = st.session_state.student_answer

    if not text_to_speak:
        st.session_state.gemini_error = "Please ask a question first."
        return False

    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[
                {
                    "type": "user_input",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Explain this to a school student in a "
                                "friendly, clear and natural teacher voice.\n\n"
                                + text_to_speak
                            ),
                            "annotations": [
                                {
                                    "type": "speech_metadata",
                                    "style": "friendly, clear and encouraging",
                                }
                            ],
                        }
                    ],
                }
            ],
            response_format={
                "type": "audio",
                "mime_type": "audio/wav",
            },
            generation_config={
                "speech_config": [
                    {"voice": "Kore"}
                ]
            },
        )

        if interaction and interaction.output_audio and interaction.output_audio.data:
            st.session_state.voice_audio = base64.b64decode(
                interaction.output_audio.data
            )
            st.session_state.gemini_error = ""
            return True

        st.session_state.gemini_error = "No voice audio was returned."
        return False

    except Exception as error:
        st.session_state.gemini_error = str(error)
        return False


def generate_visual_for_answer():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available."
        return False

    prompt = f"""
Create a simple educational illustration specifically for the selected learning topic.
The image must visually teach the exact concept asked in the student question and explained in the answer.

Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Question:
{st.session_state.student_question}

Answer:
{st.session_state.student_answer}

Requirements:
- Educational and age-appropriate.
- Clear and easy to understand.
- Friendly learning-app style.
- Show the exact topic/concept visually based on the student question and answer.
- The generated visual must be directly related to the selected topic, not a generic school image.
- Avoid unnecessary text.
- Avoid complicated diagrams.
- Use a clean 16:9 composition.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",
            input=prompt,
            response_format={
                "type": "image",
                "aspect_ratio": "16:9",
                "image_size": "1K",
            },
        )

        if interaction and interaction.output_image and interaction.output_image.data:
            st.session_state.generated_visual = base64.b64decode(
                interaction.output_image.data
            )
            st.session_state.gemini_error = ""
            return True

        st.session_state.gemini_error = "No learning image was returned."
        return False

    except Exception as error:
        st.session_state.gemini_error = str(error)
        return False


def generate_video_for_answer():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available."
        return False

    prompt = f"""
Create a short educational animation specifically for the selected learning topic.
The animation must visually explain the exact concept in the student question and answer.

Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Question:
{st.session_state.student_question}

Answer:
{st.session_state.student_answer}

Requirements:
- Make the exact selected topic/concept easy to understand visually.
- The animation must be directly based on the selected topic, question, and answer, not a generic educational animation.
- Friendly educational animation.
- Age-appropriate.
- Simple classroom-learning style.
- Use clear visual actions rather than lots of on-screen text.
- Create a short explanation suitable for a learning app.
"""

    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                resolution="720p",
            ),
        )

        max_polls = 90
        polls = 0

        while not operation.done and polls < max_polls:
            time.sleep(10)
            polls += 1
            operation = client.operations.get(operation)

        if not operation.done:
            st.session_state.gemini_error = (
                "Veo video generation is taking longer than expected. "
                "Please try again after a short wait."
            )
            return False

        operation_error = getattr(operation, "error", None)
        if operation_error:
            st.session_state.gemini_error = f"Veo operation error: {operation_error}"
            return False

        response = getattr(operation, "response", None)
        generated_videos = getattr(response, "generated_videos", None) if response else None

        if not generated_videos:
            st.session_state.gemini_error = "Veo finished, but no video was returned."
            return False

        generated_video = generated_videos[0]

        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False
        ) as temp_file:
            video_path = temp_file.name

        client.files.download(
            file=generated_video.video,
            destination=video_path,
        )

        st.session_state.generated_video = Path(video_path).read_bytes()
        st.session_state.gemini_error = ""
        return True

    except Exception as error:
        st.session_state.gemini_error = str(error)
        return False


# =========================================================
# TOPIC LEARNING CHOICES
# =========================================================

def generate_topic_summary():

    prompt = f"""
Create a short and easy answer for a school student.

Board: {st.session_state.board}
Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Lesson explanation:
{st.session_state.explanation}

Quick summary:
{st.session_state.summary}

Requirements:
- Explain only the selected topic.
- Use very simple student-friendly language.
- Give 3 to 5 short points.
- Keep the important ideas only.
- Do not add unrelated information.
"""

    answer, error = ask_gemini(prompt)

    if answer:
        st.session_state.topic_summary = answer
        st.session_state.gemini_error = ""
        return True

    st.session_state.gemini_error = error
    return False


def generate_topic_voice():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available."
        return False

    text_to_speak = (
        f"Topic: {st.session_state.topic}.\n\n"
        f"{st.session_state.explanation}\n\n"
        f"Quick summary: {st.session_state.summary}\n\n"
        f"Example: {st.session_state.example}"
    )

    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash-tts",
            input=[
                {
                    "type": "user_input",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a friendly school teacher. "
                                "Explain this exact topic clearly, slowly "
                                "and warmly to a student.\n\n"
                                + text_to_speak
                            ),
                            "annotations": [
                                {
                                    "type": "speech_metadata",
                                    "style": "friendly, clear and encouraging",
                                }
                            ],
                        }
                    ],
                }
            ],
            response_format={
                "type": "audio",
                "mime_type": "audio/wav",
            },
            generation_config={
                "speech_config": [
                    {"voice": "Kore"}
                ]
            },
        )

        if interaction and interaction.output_audio and interaction.output_audio.data:
            st.session_state.topic_voice_audio = base64.b64decode(
                interaction.output_audio.data
            )
            st.session_state.gemini_error = ""
            return True

        st.session_state.gemini_error = "No voice audio was returned."
        return False

    except Exception as error:
        st.session_state.gemini_error = str(error)
        return False


def generate_topic_visual():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available."
        return False

    prompt = f"""
Create a beautiful educational illustration that teaches the exact topic below.

Board: {st.session_state.board}
Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Lesson explanation:
{st.session_state.explanation}

The image MUST be directly about the selected topic and its main concept.
It must not be a generic school image.

Requirements:
- Educational and age-appropriate.
- Simple and easy to understand.
- Friendly learning-app style.
- Show the main concept clearly.
- Use visual examples where useful.
- Avoid unnecessary text.
- Avoid complicated diagrams.
- Use a clean 16:9 composition.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",
            input=prompt,
            response_format={
                "type": "image",
                "aspect_ratio": "16:9",
                "image_size": "1K",
            },
        )

        if interaction and interaction.output_image and interaction.output_image.data:
            st.session_state.topic_visual = base64.b64decode(
                interaction.output_image.data
            )
            st.session_state.gemini_error = ""
            return True

        st.session_state.gemini_error = "No learning image was returned."
        return False

    except Exception as error:
        st.session_state.gemini_error = str(error)
        return False


def generate_topic_video():

    if client is None:
        st.session_state.gemini_error = "Gemini client is not available. Check GEMINI_API_KEY in .env."
        return False

    prompt = f"""
Create a short educational AI video that explains the exact topic below.

Board: {st.session_state.board}
Class: {st.session_state.class_level}
Subject: {st.session_state.subject}
Topic: {st.session_state.topic}

Lesson explanation:
{st.session_state.explanation}

Quick summary:
{st.session_state.summary}

Example:
{st.session_state.example}

Requirements:
- The video must directly teach the selected topic.
- Make the concept easy for a student of this class to understand.
- Use clear visual actions and examples.
- Keep it friendly and educational.
- Do not make a generic school video.
- Avoid lots of on-screen text.
- Use a simple learning-app style.
- Keep the explanation concise because this is a short learning video.
"""

    try:
        # Veo generation is a long-running operation.
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                resolution="720p",
            ),
        )

        # Poll until the Veo operation finishes.
        # A maximum wait prevents the Streamlit page from hanging forever.
        max_polls = 90
        polls = 0

        while not operation.done and polls < max_polls:
            time.sleep(10)
            polls += 1
            operation = client.operations.get(operation)

        if not operation.done:
            st.session_state.gemini_error = (
                "Veo video generation is taking longer than expected. "
                "Please try again after a short wait."
            )
            return False

        # Some SDK responses expose the failure through operation.error.
        operation_error = getattr(operation, "error", None)
        if operation_error:
            st.session_state.gemini_error = f"Veo operation error: {operation_error}"
            return False

        response = getattr(operation, "response", None)
        generated_videos = getattr(response, "generated_videos", None) if response else None

        if not generated_videos:
            st.session_state.gemini_error = (
                "Veo finished, but no video was returned. "
                "This can happen when video generation is not enabled for the API key/project "
                "or when the model request is rejected by the service."
            )
            return False

        generated_video = generated_videos[0]
        video_file = getattr(generated_video, "video", None)

        if video_file is None:
            st.session_state.gemini_error = "Veo returned a result, but the video file was missing."
            return False

        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False
        ) as temp_file:
            video_path = temp_file.name

        client.files.download(
            file=video_file,
            destination=video_path,
        )

        video_bytes = Path(video_path).read_bytes()

        if not video_bytes:
            st.session_state.gemini_error = "The generated video file was empty."
            return False

        st.session_state.topic_video = video_bytes
        st.session_state.gemini_error = ""
        return True

    except Exception as error:
        st.session_state.gemini_error = (
            "Veo video generation failed:\n\n"
            + str(error)
            + "\n\n"
            "If this says quota, billing, permission, or model access, "
            "the problem is with Gemini API access rather than Streamlit."
        )
        return False


# =========================================================
# JSON EXTRACTION
# =========================================================

def extract_json(text):

    if not text:

        return None

    text = text.strip()

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"```\s*$",
        "",
        text
    )

    try:

        return json.loads(text)

    except Exception:

        pass

    array_start = text.find("[")

    if array_start != -1:

        array_end = text.rfind("]")

        if array_end != -1:

            possible = text[
                array_start:
                array_end + 1
            ]

            try:

                return json.loads(possible)

            except Exception:

                pass

    return None


# =========================================================
# GENERATE QUIZ
# =========================================================

def generate_quiz():

    prompt = f"""
Create exactly 3 multiple-choice questions
for a school learning game.

Board:
{st.session_state.board}

Class:
{st.session_state.class_level}

Subject:
{st.session_state.subject}

Topic:
{st.session_state.topic}

Difficulty:

Question 1 = Easy
Question 2 = Medium
Question 3 = Medium

Return ONLY valid JSON.

Use exactly this structure:

[
  {{
    "question": "Question text",
    "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
    ],
    "answer": 0,
    "explanation": "Short explanation"
  }}
]

The answer must be the zero-based option number.

Do not add any text outside the JSON.
"""

    answer, error = ask_gemini(prompt)

    if not answer:

        st.session_state.gemini_error = error

        return False

    data = extract_json(answer)

    if not isinstance(data, list):

        st.session_state.gemini_error = (
            "Gemini returned an invalid quiz format."
        )

        return False

    if len(data) != 3:

        st.session_state.gemini_error = (
            "Gemini did not return exactly 3 questions."
        )

        return False

    valid_questions = []

    for item in data:

        if not isinstance(item, dict):

            continue

        question = item.get("question")

        options = item.get("options")

        correct = item.get("answer")

        if (
            question
            and isinstance(options, list)
            and len(options) == 4
            and isinstance(correct, int)
            and 0 <= correct <= 3
        ):

            valid_questions.append(
                {
                    "question": question,
                    "options": options,
                    "answer": correct,
                    "explanation": item.get(
                        "explanation",
                        "Good job! Keep learning."
                    )
                }
            )

    if len(valid_questions) != 3:

        st.session_state.gemini_error = (
            "Gemini returned incomplete quiz questions."
        )

        return False

    st.session_state.quiz_questions = (
        valid_questions
    )

    st.session_state.quiz_index = 0

    st.session_state.quiz_score = 0

    st.session_state.quiz_answered = False

    st.session_state.quiz_feedback = ""

    st.session_state.quiz_generated = True

    st.session_state.gemini_error = ""

    return True


# =========================================================
# GENERATE FINAL CHALLENGE
# =========================================================

def generate_challenge():

    prompt = f"""
Create exactly 3 harder application
and reasoning questions.

Board:
{st.session_state.board}

Class:
{st.session_state.class_level}

Subject:
{st.session_state.subject}

Topic:
{st.session_state.topic}

The questions should test whether
the student can APPLY the concept,
not just remember a definition.

Return ONLY valid JSON.

Use exactly this structure:

[
  {{
    "question": "Question text",
    "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
    ],
    "answer": 0,
    "explanation": "Short explanation"
  }}
]

The answer must be the zero-based option number.

Do not add any text outside the JSON.
"""

    answer, error = ask_gemini(prompt)

    if not answer:

        st.session_state.gemini_error = error

        return False

    data = extract_json(answer)

    if not isinstance(data, list):

        st.session_state.gemini_error = (
            "Gemini returned an invalid challenge format."
        )

        return False

    if len(data) != 3:

        st.session_state.gemini_error = (
            "Gemini did not return exactly 3 challenges."
        )

        return False

    valid_questions = []

    for item in data:

        if not isinstance(item, dict):

            continue

        question = item.get("question")

        options = item.get("options")

        correct = item.get("answer")

        if (
            question
            and isinstance(options, list)
            and len(options) == 4
            and isinstance(correct, int)
            and 0 <= correct <= 3
        ):

            valid_questions.append(
                {
                    "question": question,
                    "options": options,
                    "answer": correct,
                    "explanation": item.get(
                        "explanation",
                        "Keep practicing!"
                    )
                }
            )

    if len(valid_questions) != 3:

        st.session_state.gemini_error = (
            "Gemini returned incomplete challenge questions."
        )

        return False

    st.session_state.challenge_questions = (
        valid_questions
    )

    st.session_state.challenge_index = 0

    st.session_state.challenge_score = 0

    st.session_state.challenge_answered = False

    st.session_state.challenge_feedback = ""

    st.session_state.challenge_generated = True

    st.session_state.gemini_error = ""

    return True


# =========================================================
# RESET ADVENTURE
# =========================================================

def reset_adventure():

    for key, value in DEFAULT_STATE.items():

        st.session_state[key] = value


# =========================================================
# HOME
# =========================================================

def show_home():

    with st.container(border=True):

        st.title("🚀 LEARNQUEST AI")

        st.subheader(
            "Turn Learning Into An Adventure"
        )

        st.write(
            "🌟 Learn • Play • Discover"
        )

    with st.container(border=True):

        st.header(
            "🎮 Your Learning Adventure"
        )

        st.write(
            "Learn any topic through an "
            "interactive AI-powered adventure."
        )

        st.write("📖 Learn the topic")
        st.write("🤖 Ask the AI Tutor")
        st.write("🧠 Complete a quiz")
        st.write("⚔️ Solve harder challenges")
        st.write("⭐ Earn XP")
        st.write("🏆 Complete your quest")

        st.write("")

        if st.button(
            "🚀 START ADVENTURE",
            use_container_width=True
        ):

            st.session_state.page = "setup"
            st.rerun()


# =========================================================
# SETUP
# =========================================================

def show_setup():

    with st.container(border=True):

        st.title("🧑‍🏫 Adventure Setup")

        st.write(
            "Choose your curriculum, class, "
            "subject and learning topic."
        )

    with st.container(border=True):

        board = st.selectbox(
            "📚 Board / Curriculum",
            [
                "CBSE",
                "State Board",
                "ICSE",
                "Other"
            ]
        )

        class_level = st.selectbox(
            "🎓 Class",
            [
                str(i)
                for i in range(1, 13)
            ]
        )

        class_number = int(
            class_level
        )

        if class_number <= 5:

            subjects = PRIMARY_SUBJECTS

        elif class_number <= 10:

            subjects = MIDDLE_SUBJECTS

        else:

            subjects = HIGHER_SUBJECTS

        subject = st.selectbox(
            "📖 Subject",
            subjects
        )

        topic = st.text_input(
            "🔍 Enter Topic",
            placeholder=(
                "Example: 2 digit additions"
            )
        )

        st.write("")

        if st.button(
            "🌟 START QUEST",
            use_container_width=True
        ):

            if not topic.strip():

                st.warning(
                    "Please enter a topic first."
                )

                return

            st.session_state.board = board

            st.session_state.class_level = (
                class_level
            )

            st.session_state.subject = (
                subject
            )

            st.session_state.topic = (
                topic.strip()
            )

            st.session_state.page = (
                "academy"
            )

            st.session_state.mission = 1

            st.session_state.explanation = ""

            st.session_state.summary = ""

            st.session_state.example = ""

            st.session_state.student_question = ""

            st.session_state.student_answer = ""

            st.session_state.student_answer_error = ""

            st.session_state.gemini_error = ""

            st.session_state.quiz_questions = []

            st.session_state.challenge_questions = []

            st.session_state.quiz_index = 0

            st.session_state.challenge_index = 0

            st.session_state.quiz_score = 0

            st.session_state.challenge_score = 0

            st.session_state.xp = 0

            st.session_state.quiz_answered = False

            st.session_state.challenge_answered = False

            st.session_state.quiz_feedback = ""

            st.session_state.challenge_feedback = ""

            st.session_state.quest_complete = False
            st.session_state.result_celebrated = False

            st.session_state.lesson_generated = False

            st.session_state.quiz_generated = False

            st.session_state.challenge_generated = False

            st.session_state.topic_learning_mode = ""
            st.session_state.topic_voice_audio = None
            st.session_state.topic_summary = ""
            st.session_state.topic_visual = None
            st.session_state.topic_video = None

            st.rerun()


# =========================================================
# ACADEMY
# =========================================================

def show_academy():

    with st.container(border=True):

        st.title(
            "🏰 LEARNQUEST ACADEMY"
        )

        st.subheader(
            f"📜 Quest: Master "
            f"{st.session_state.topic}"
        )

        progress_values = {
            1: 0.33,
            2: 0.66,
            3: 1.0
        }

        st.progress(
            progress_values.get(
                st.session_state.mission,
                0.33
            )
        )

        st.write(
            f"Mission "
            f"{st.session_state.mission} "
            f"of 3"
        )

    st.write("")

    if st.session_state.mission == 1:

        show_mission_1()

    elif st.session_state.mission == 2:

        show_mission_2()

    elif st.session_state.mission == 3:

        show_mission_3()


# =========================================================
# MISSION 1
# =========================================================

def show_mission_1():

    with st.container(border=True):

        st.header(
            "⚔️ Mission 1 — Learn the Topic"
        )

        st.write(
            f"Your first mission is to understand **{st.session_state.topic}**."
        )

    if not st.session_state.lesson_generated:

        with st.spinner(
            "🤖 AI Tutor is preparing your lesson..."
        ):

            success = generate_learning_content()

        if not success:

            st.error(
                "The AI lesson could not be generated."
            )

            if st.session_state.gemini_error:
                st.code(st.session_state.gemini_error)

            if st.button(
                "🔄 TRY AGAIN",
                use_container_width=True
            ):
                st.rerun()

        else:
            st.rerun()

        return

    # -----------------------------------------------------
    # FOUR LEARNING CHOICES - SHOWN AFTER TOPIC SETUP
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader(
            "✨ How do you want to learn this topic?"
        )

        st.caption(
            "Choose one option below to generate the answer in that format."
        )

    # Row 1
    col1, col2 = st.columns(2, gap="medium")

    with col1:

        with st.container(border=True):

            st.subheader("🔊 Voice")
            st.write("Listen to answer")

            if st.button(
                "🔊 USE VOICE",
                key="topic_use_voice",
                use_container_width=True
            ):

                st.session_state.topic_learning_mode = "voice"

                with st.spinner(
                    "🎙️ AI teacher is preparing the topic voice..."
                ):

                    success = generate_topic_voice()

                if success:
                    st.rerun()
                else:
                    st.error(
                        "Voice explanation could not be generated."
                    )
                    if st.session_state.gemini_error:
                        st.write("Technical details:")
                        st.code(st.session_state.gemini_error)

    with col2:

        with st.container(border=True):

            st.subheader("📝 Summary Text")
            st.write("Short answer")

            if st.button(
                "📝 USE SUMMARY",
                key="topic_use_summary",
                use_container_width=True
            ):

                st.session_state.topic_learning_mode = "summary"

                with st.spinner(
                    "📝 AI is preparing a short answer..."
                ):

                    success = generate_topic_summary()

                if success:
                    st.rerun()
                else:
                    st.error(
                        "Summary could not be generated."
                    )
                    if st.session_state.gemini_error:
                        st.write("Technical details:")
                        st.code(st.session_state.gemini_error)

    st.write("")

    # Row 2
    col3, col4 = st.columns(2, gap="medium")

    with col3:

        with st.container(border=True):

            st.subheader("🎨 Image")
            st.write("AI visual")

            if st.button(
                "🎨 GENERATE IMAGE",
                key="topic_generate_image",
                use_container_width=True
            ):

                st.session_state.topic_learning_mode = "image"

                with st.spinner(
                    "🎨 AI is creating a visual for your topic..."
                ):

                    success = generate_topic_visual()

                if success:
                    st.rerun()
                else:
                    st.error(
                        "Learning image could not be generated."
                    )
                    if st.session_state.gemini_error:
                        st.write("Technical details:")
                        st.code(st.session_state.gemini_error)

    with col4:

        # Video option intentionally removed.
        # The fourth slot remains empty so the existing 2-column layout
        # and the other learning choices are not disturbed.
        st.empty()

    # -----------------------------------------------------
    # SELECTED TOPIC RESULT
    # -----------------------------------------------------

    if st.session_state.topic_learning_mode == "summary":

        if st.session_state.topic_summary:

            with st.container(border=True):

                st.subheader("📝 Short Answer")
                st.write(st.session_state.topic_summary)

    elif st.session_state.topic_learning_mode == "voice":

        if st.session_state.topic_voice_audio:

            with st.container(border=True):

                st.subheader("🔊 Voice Answer")
                st.write(
                    f"AI explanation for: {st.session_state.topic}"
                )
                st.audio(
                    st.session_state.topic_voice_audio,
                    format="audio/wav"
                )

    elif st.session_state.topic_learning_mode == "image":

        if st.session_state.topic_visual:

            with st.container(border=True):

                st.subheader("🎨 AI Visual")
                st.image(
                    st.session_state.topic_visual,
                    use_container_width=True,
                    caption=st.session_state.topic
                )

    st.write("")

    # -----------------------------------------------------
    # EXISTING LESSON CONTENT
    # -----------------------------------------------------

    with st.container(border=True):

        st.subheader(
            f"🤖 AI Tutor — {st.session_state.topic}"
        )

        st.write(
            st.session_state.explanation
        )

    if st.session_state.summary:

        with st.container(border=True):

            st.subheader("✨ Quick Summary")

            st.write(
                st.session_state.summary
            )

    if st.session_state.example:

        with st.container(border=True):

            st.subheader("💡 Easy Example")

            st.info(
                st.session_state.example
            )

    st.write("")

    with st.container(border=True):

        st.subheader("💬 Ask Your AI Tutor")

        question = st.text_input(
            "Ask anything about this topic",
            placeholder="Example: Why do we carry 1 in addition?",
            key="student_question_input"
        )

        if st.button(
            "🤖 ASK AI TUTOR",
            use_container_width=True
        ):

            if not question.strip():

                st.warning("Please type a question first.")

            else:

                st.session_state.student_question = question.strip()
                st.session_state.student_answer = ""
                st.session_state.answer_summary = ""
                st.session_state.learning_mode = ""
                st.session_state.voice_audio = None
                st.session_state.generated_visual = None
                st.session_state.generated_video = None

                with st.spinner(
                    "🤖 AI Tutor is thinking..."
                ):

                    success = ask_ai_tutor(
                        question.strip()
                    )

                if success:
                    st.rerun()

                else:
                    st.error(
                        "The AI Tutor could not answer right now."
                    )

                    if st.session_state.student_answer_error:
                        st.code(
                            st.session_state.student_answer_error
                        )

    if st.session_state.student_answer:

        with st.container(border=True):

            st.subheader(
                "🧑‍🏫 AI Tutor's Explanation"
            )

            st.write(
                st.session_state.student_answer
            )

    st.write("")

    with st.container(border=True):

        st.subheader("🔐 Ready for the Quiz?")

        st.write(
            "Once you understand the topic, unlock Mission 2."
        )

        if st.button(
            "✅ I UNDERSTAND — UNLOCK MISSION 2",
            use_container_width=True
        ):

            st.session_state.mission = 2
            st.session_state.quiz_generated = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_answered = False
            st.session_state.quiz_feedback = ""

            st.rerun()


# =========================================================
# MISSION 2
# =========================================================

def show_mission_2():

    with st.container(border=True):

        st.header(
            "🔮 Mission 2 — Topic Quiz"
        )

        st.write(
            "Answer 3 questions to earn XP."
        )

        st.info(
            "⭐ Correct answer = +10 XP"
        )

    if not st.session_state.quiz_generated:

        with st.spinner(
            "🧠 AI Tutor is creating your quiz..."
        ):

            success = generate_quiz()

        if not success:

            st.error(
                "The quiz could not be generated."
            )

            if st.session_state.gemini_error:

                st.code(
                    st.session_state.gemini_error
                )

            if st.button(
                "🔄 TRY QUIZ AGAIN",
                use_container_width=True
            ):

                st.rerun()

        else:

            st.rerun()

        return

    questions = (
        st.session_state.quiz_questions
    )

    index = (
        st.session_state.quiz_index
    )

    if index >= len(questions):

        st.success(
            "🎉 Mission 2 Complete!"
        )

        st.write(
            f"Quiz Score: "
            f"{st.session_state.quiz_score} / 3"
        )

        st.write(
            f"⭐ XP: "
            f"{st.session_state.xp}"
        )

        with st.container(border=True):

            st.subheader(
                "🔓 Mission 3 Unlocked!"
            )

            st.write(
                "You are ready for the final challenge."
            )

            if st.button(
                "🏆 START MISSION 3",
                use_container_width=True
            ):

                st.session_state.mission = 3

                st.session_state.challenge_generated = False

                st.session_state.challenge_questions = []

                st.session_state.challenge_index = 0

                st.session_state.challenge_score = 0

                st.session_state.challenge_answered = False

                st.session_state.challenge_feedback = ""

                st.rerun()

        return

    current = questions[index]

    st.write(
        f"Question {index + 1} of 3"
    )

    st.progress(
        (index + 1) / 3
    )

    with st.container(border=True):

        st.subheader(
            current["question"]
        )

        selected = st.radio(
            "Choose your answer:",
            current["options"],
            index=None,
            key=f"quiz_option_{index}"
        )

        if not st.session_state.quiz_answered:

            if st.button(
                "✅ SUBMIT ANSWER",
                use_container_width=True
            ):

                if selected is None:

                    st.warning(
                        "Please select an answer."
                    )

                else:

                    selected_index = (
                        current["options"].index(
                            selected
                        )
                    )

                    correct_index = (
                        current["answer"]
                    )

                    if selected_index == correct_index:

                        st.session_state.quiz_score += 1

                        st.session_state.xp += 10

                        st.session_state.quiz_feedback = (
                            "🎉 Correct! +10 XP\n\n"
                            + current["explanation"]
                        )

                    else:

                        correct_option = (
                            current["options"][
                                correct_index
                            ]
                        )

                        st.session_state.quiz_feedback = (
                            "❌ Not quite.\n\n"
                            f"Correct answer: "
                            f"{correct_option}\n\n"
                            + current["explanation"]
                        )

                    st.session_state.quiz_answered = True

                    st.rerun()

        else:

            if "Correct!" in (
                st.session_state.quiz_feedback
            ):

                st.success(
                    st.session_state.quiz_feedback
                )

            else:

                st.warning(
                    st.session_state.quiz_feedback
                )

            if st.button(
                "➡️ NEXT QUESTION",
                use_container_width=True
            ):

                st.session_state.quiz_index += 1

                st.session_state.quiz_answered = False

                st.session_state.quiz_feedback = ""

                st.rerun()


# =========================================================
# MISSION 3
# =========================================================

def show_mission_3():

    with st.container(border=True):

        st.header(
            "🏆 Mission 3 — Final Challenge"
        )

        st.write(
            "Now apply what you learned."
        )

        st.info(
            "🎯 Correct answer = +20 XP"
        )

    if not st.session_state.challenge_generated:

        with st.spinner(
            "🧠 AI Tutor is creating your final challenge..."
        ):

            success = generate_challenge()

        if not success:

            st.error(
                "The final challenge could not be generated."
            )

            if st.session_state.gemini_error:

                st.code(
                    st.session_state.gemini_error
                )

            if st.button(
                "🔄 TRY CHALLENGE AGAIN",
                use_container_width=True
            ):

                st.rerun()

        else:

            st.rerun()

        return

    questions = (
        st.session_state.challenge_questions
    )

    index = (
        st.session_state.challenge_index
    )

    if index >= len(questions):

        st.session_state.quest_complete = True

        st.session_state.page = "result"

        st.rerun()

        return

    current = questions[index]

    st.write(
        f"Challenge {index + 1} of 3"
    )

    st.progress(
        (index + 1) / 3
    )

    with st.container(border=True):

        st.subheader(
            current["question"]
        )

        selected = st.radio(
            "Choose your answer:",
            current["options"],
            index=None,
            key=f"challenge_option_{index}"
        )

        if not st.session_state.challenge_answered:

            if st.button(
                "🎯 SUBMIT CHALLENGE",
                use_container_width=True
            ):

                if selected is None:

                    st.warning(
                        "Please select an answer."
                    )

                else:

                    selected_index = (
                        current["options"].index(
                            selected
                        )
                    )

                    correct_index = (
                        current["answer"]
                    )

                    if selected_index == correct_index:

                        st.session_state.challenge_score += 1

                        st.session_state.xp += 20

                        st.session_state.challenge_feedback = (
                            "🎉 Excellent! +20 XP\n\n"
                            + current["explanation"]
                        )

                    else:

                        correct_option = (
                            current["options"][
                                correct_index
                            ]
                        )

                        st.session_state.challenge_feedback = (
                            "❌ Good attempt.\n\n"
                            f"Correct answer: "
                            f"{correct_option}\n\n"
                            + current["explanation"]
                        )

                    st.session_state.challenge_answered = True

                    st.rerun()

        else:

            if "Excellent!" in (
                st.session_state.challenge_feedback
            ):

                st.success(
                    st.session_state.challenge_feedback
                )

            else:

                st.warning(
                    st.session_state.challenge_feedback
                )

            if st.button(
                "➡️ NEXT CHALLENGE",
                use_container_width=True
            ):

                st.session_state.challenge_index += 1

                st.session_state.challenge_answered = False

                st.session_state.challenge_feedback = ""

                st.rerun()


# =========================================================
# RESULT
# =========================================================

def show_result():

    # ---------------------------------------------------------
    # FINAL PAGE ONLY: soft pastel text boxes
    # ---------------------------------------------------------
    st.markdown(
        """
        <style>

        /* These styles are loaded only while the Quest Complete
           page is displayed, so other pages are not changed. */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(135deg, #fffaff, #f8f5ff) !important;
            background-color: #fffaff !important;
            border: 2px solid #eadfff !important;
            box-shadow: 0 8px 24px rgba(140,120,180,0.10) !important;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] p,
        div[data-testid="stVerticalBlockBorderWrapper"] h1,
        div[data-testid="stVerticalBlockBorderWrapper"] h2,
        div[data-testid="stVerticalBlockBorderWrapper"] h3,
        div[data-testid="stVerticalBlockBorderWrapper"] label {
            color: #4d496b !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    total_correct = (
        st.session_state.quiz_score
        + st.session_state.challenge_score
    )

    total_questions = 6

    percentage = (
        total_correct / total_questions
    ) * 100

    # Performance bands requested for the final page:
    # <50 = relearn, 50-79 = medium, >=80 = excellent.
    if percentage < 50:

        performance = "poor"
        badge = "🌱 Keep Learning"
        title = "💪 Let's Learn It Again!"
        message = (
            "No worries! You have finished the quest, and now you know "
            "exactly what to practise. Relearn the topic and try the quest again."
        )

    elif percentage < 80:

        performance = "medium"
        badge = "😊 Good Progress"
        title = "😊 Nice Work!"
        message = (
            "You understand a good part of the topic. A little more practice "
            "can help you become even stronger."
        )

    else:

        performance = "excellent"
        badge = "🏆 Quest Master"
        title = "💖 Amazing Work!"
        message = (
            "Excellent performance! You understood the topic and handled the "
            "challenges really well."
        )

        # Celebrate excellent performance once when the result is first shown.
        if not st.session_state.get("result_celebrated", False):
            st.balloons()
            st.session_state.result_celebrated = True

    with st.container(border=True):

        st.title("🎉 QUEST COMPLETE!")

        st.subheader(title)

        if performance == "poor":
            st.error(
                "👎 " + message
            )
        elif performance == "medium":
            st.info(
                "😊 " + message
            )
        else:
            st.success(
                "💖 " + message + " 💕"
            )

        st.subheader(badge)

        # Main result information stays on the left;
        # the new progress pie chart appears on the right.
        left_col, right_col = st.columns([1.35, 1])

        with left_col:

            st.write(
                f"📚 Topic: {st.session_state.topic}"
            )

            st.write(
                f"🎓 Class: {st.session_state.class_level}"
            )

            st.write(
                f"📖 Subject: {st.session_state.subject}"
            )

            st.metric(
                "⭐ Total XP",
                st.session_state.xp
            )

            st.metric(
                "🧠 Quiz Score",
                f"{st.session_state.quiz_score} / 3"
            )

            st.metric(
                "🏆 Final Challenge",
                f"{st.session_state.challenge_score} / 3"
            )

            st.metric(
                "📊 Overall Score",
                f"{total_correct} / {total_questions}"
            )

            st.progress(
                percentage / 100
            )

            st.write(
                f"Overall performance: {percentage:.0f}%"
            )

        with right_col:

            st.subheader("📈 Your Progress")

            correct_count = total_correct
            incorrect_count = total_questions - total_correct

            pie_data = [
                {
                    "result": "Correct",
                    "questions": correct_count
                },
                {
                    "result": "To Improve",
                    "questions": incorrect_count
                }
            ]

            pie_chart = {
                "data": {"values": pie_data},
                "mark": {
                    "type": "arc",
                    "innerRadius": 58,
                    "stroke": "#ffffff",
                    "strokeWidth": 3
                },
                "encoding": {
                    "theta": {
                        "field": "questions",
                        "type": "quantitative"
                    },
                    "color": {
                        "field": "result",
                        "type": "nominal",
                        "scale": {
                            "domain": ["Correct", "To Improve"],
                            "range": ["#2EAD65", "#E94F64"]
                        },
                        "legend": {
                            "title": ""
                        }
                    },
                    "tooltip": [
                        {
                            "field": "result",
                            "type": "nominal",
                            "title": "Result"
                        },
                        {
                            "field": "questions",
                            "type": "quantitative",
                            "title": "Questions"
                        }
                    ]
                },
                "view": {"stroke": None},
                "width": "container",
                "height": 280
            }

            st.vega_lite_chart(
                pie_chart,
                use_container_width=True
            )

            st.caption(
                f"{total_correct} correct out of {total_questions} questions"
            )

    st.write("")

    if performance == "poor":

        with st.container(border=True):

            st.subheader("👎 Relearn the Topic")

            st.write(
                "Your score is below 50%. Go back to Mission 1, review the "
                "lesson, and then try the quiz and final challenge again."
            )

            if st.button(
                "📖 RELEARN TOPIC — GO TO MISSION 1",
                use_container_width=True,
                type="primary"
            ):

                st.session_state.page = "academy"
                st.session_state.mission = 1
                st.session_state.lesson_generated = True
                st.session_state.topic_learning_mode = ""
                st.session_state.topic_voice_audio = None
                st.session_state.topic_summary = ""
                st.session_state.topic_visual = None
                st.session_state.topic_video = None
                st.session_state.quiz_index = 0
                st.session_state.challenge_index = 0
                st.session_state.quiz_score = 0
                st.session_state.challenge_score = 0
                st.session_state.xp = 0
                st.session_state.quiz_generated = False
                st.session_state.challenge_generated = False
                st.session_state.quiz_questions = []
                st.session_state.challenge_questions = []
                st.session_state.quiz_answered = False
                st.session_state.challenge_answered = False
                st.session_state.quiz_feedback = ""
                st.session_state.challenge_feedback = ""
                st.session_state.quest_complete = False
                st.session_state.result_celebrated = False
                st.rerun()

    elif performance == "medium":

        with st.container(border=True):

            st.subheader("😊 Medium Performance")

            st.write(
                "You are on the right track. Keep practising and you can reach "
                "the excellent level next time."
            )

    else:

        with st.container(border=True):

            st.subheader("💖 Excellent Performance")

            st.write(
                "You have successfully completed the adventure at an excellent level!"
            )

    st.write("")

    if st.button(
        "🔄 START A NEW ADVENTURE",
        use_container_width=True,
        type="primary"
    ):

        reset_adventure()
        st.rerun()


# =========================================================
# PAGE ROUTING
# =========================================================

# Apply the background AFTER the selected class is stored in
# session state. This is important because the class is chosen
# on the Setup page after the app first loads.
apply_background()
apply_page_theme(st.session_state.page)

if st.session_state.page == "home":

    show_home()

elif st.session_state.page == "setup":

    show_setup()

elif st.session_state.page == "academy":

    show_academy()

elif st.session_state.page == "result":

    show_result()