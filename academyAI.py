import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from json_loader import load_json

def main():
    load_dotenv()
    gen_key = os.getenv("GEMINI_API_KEY")

    if not gen_key:
        st.error("API key not found. Please set the GEMINI_API in the environment.")
        return

    genai.configure(api_key=gen_key)

    # Main Layout
    st.title("🎓 NEUC Academic Consultant")
    st.markdown("Welcome! Let’s help you find the right course based on your personality and interests.")

    # Tabs for Navigation
    tabs = st.tabs(["Introduction", "Questionnaire", "Recommendations"])

    # Introduction Tab
    with tabs[0]:
        st.header("Introduction")
        st.write(
            "Tell us a bit about yourself to get personalized recommendations. "
            "Your responses will help us tailor our course suggestions."
        )
        user_description = st.text_area("Describe your current situation (optional)", "")

    # Questionnaire Tab
    with tabs[1]:
        st.header("Personality Check")
        st.write("Answer a few questions to help us understand your personality type.")

        # Using Expander for Grouped Questions
        with st.expander("Answer the following questions"):
            q1 = st.radio("Do you prefer:", ["Working independently", "Working in groups"])
            q2 = st.radio("Are you more:", ["Analytical and logical", "Empathetic and caring"])
            q3 = st.radio("When solving problems, do you prefer:", ["Structured plans", "Flexible approaches"])
            q4 = st.radio("Do you feel energized after social interactions?", ["Yes", "No"])
            q5 = st.radio("When making decisions, do you rely more on:", ["Facts", "Feelings"])
            q6 = st.radio("Do you prefer to:", ["Plan ahead", "Go with the flow"])
            q7 = st.radio("When starting a new project, do you:", ["Dive in", "Plan carefully"])
            q8 = st.radio("Do you focus on:", ["Practical realities", "Abstract possibilities"])

        # Scoring Logic
        introvert_score = (q1 == "Working independently") + (q4 == "No")
        extrovert_score = (q1 == "Working in groups") + (q4 == "Yes")
        thinking_score = (q2 == "Analytical and logical") + (q5 == "Facts")
        feeling_score = (q2 == "Empathetic and caring") + (q5 == "Feelings")
        judging_score = (q3 == "Structured plans") + (q6 == "Plan ahead") + (q7 == "Plan carefully")
        perceiving_score = (q3 == "Flexible approaches") + (q6 == "Go with the flow") + (q7 == "Dive in")
        sensing_score = (q8 == "Practical realities")
        intuition_score = (q8 == "Abstract possibilities")

        personality_type = (
            ("I" if introvert_score > extrovert_score else "E") +
            ("N" if intuition_score > sensing_score else "S") +
            ("T" if thinking_score > feeling_score else "F") +
            ("J" if judging_score > perceiving_score else "P")
        )

        st.success(f"Your personality type is **{personality_type}**.")

    # Recommendations Tab
    with tabs[2]:
        st.header("📈 Recommended Courses")
        
        json_file_path = "courses_info.json"
        json_data = load_json(json_file_path)

        def format_json_for_gemini(data):
            formatted_text = ""
            for item in data:
                formatted_text += f"**Course:** {item['Course']}\n"
                formatted_text += f"Degree: {item['Degree']}\n"
                formatted_text += f"Duration: {item['Duration(Year)']} years\n"
                formatted_text += f"Min Requirement: {item['Min Entry Requirement']}\n"
                formatted_text += f"Career Prospects: {item['Career Prospects']}\n\n"
            return formatted_text

        formatted_text = format_json_for_gemini(json_data)

        if st.button("Get Recommendations"):
            def generate_recommendations(personality, description):
                system_prompt = (
                    "You are an experienced Academic Consultant. Provide course suggestions tailored to the user's MBTI type "
                    "and any additional context they provided.\n\n"
                    f"User's personality type: {personality}\n"
                )
                if description:
                    system_prompt += f"User's situation and goals: {description}\n\n"
                system_prompt += f"Course data:\n{formatted_text}"

                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(system_prompt)
                return response.text

            response = generate_recommendations(personality_type, user_description)
            st.markdown(response)

if __name__ == "__main__":
    main()
