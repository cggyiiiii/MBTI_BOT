import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
from json_loader import load_json  # Import the load_json function

def main():
    load_dotenv()
    gen_key = os.getenv("GEMINI_API_KEY")
    
    if not gen_key:
        st.error("API key not found. Please set the GEMINI_API in the environment.")
        return
    
    genai.configure(api_key=gen_key)
    
    # Step 1: Gather Basic User Information (Optional)
    st.title("NEUC Academic Consultant")
    st.subheader("Tell us a bit about yourself (optional)")
    st.text(
        "**Please share your current situation if you'd like personalized recommendations:**\n\n"
        "What are your main concerns or challenges right now?\n"
        "What are your career aspirations or future goals?\n"
        "Any specific interests or areas where you'd like support?"
    )
    
    user_description = st.text_area("Describe your current situation (optional)", "")

    # Step 2: Expanded MBTI-like Questionnaire
    st.subheader("Personality Check")
    st.write("Answer a few quick questions to help us determine your personality type.")

    # Original Questions
    q1 = st.radio("Do you prefer:", ("Working independently", "Working in groups"))
    q2 = st.radio("Are you more:", ("Analytical and logical", "Empathetic and caring"))
    q3 = st.radio("When solving problems, do you prefer:", ("Structured plans", "Flexible, open-ended approaches"))

    # Additional Questions
    q4 = st.radio("Do you often feel energized after social interactions?", ("Yes, I feel energized and refreshed", "No, I feel drained and need time alone to recharge"))
    q5 = st.radio("When making decisions, do you rely more on:", ("Facts and data", "Your feelings and values"))
    q6 = st.radio("In your daily life, do you prefer to:", ("Plan ahead and stick to schedules", "Keep options open and go with the flow"))
    q7 = st.radio("When approaching a new project, do you:", ("Dive in and adjust as you go", "Carefully plan and organize before starting"))
    q8 = st.radio("Do you focus more on:", ("Practical, immediate realities", "Abstract possibilities and concepts"))

    # Enhanced Logic to Determine Personality Type
    introvert_score = 0
    extrovert_score = 0
    thinking_score = 0
    feeling_score = 0
    judging_score = 0
    perceiving_score = 0
    sensing_score = 0
    intuition_score = 0

    # Scoring based on responses
    introvert_score += 1 if q1 == "Working independently" else 0
    extrovert_score += 1 if q1 == "Working in groups" else 0

    thinking_score += 1 if q2 == "Analytical and logical" else 0
    feeling_score += 1 if q2 == "Empathetic and caring" else 0

    judging_score += 1 if q3 == "Structured plans" else 0
    perceiving_score += 1 if q3 == "Flexible, open-ended approaches" else 0

    extrovert_score += 1 if q4 == "Yes, I feel energized and refreshed" else 0
    introvert_score += 1 if q4 == "No, I feel drained and need time alone to recharge" else 0

    thinking_score += 1 if q5 == "Facts and data" else 0
    feeling_score += 1 if q5 == "Your feelings and values" else 0

    judging_score += 1 if q6 == "Plan ahead and stick to schedules" else 0
    perceiving_score += 1 if q6 == "Keep options open and go with the flow" else 0

    perceiving_score += 1 if q7 == "Dive in and adjust as you go" else 0
    judging_score += 1 if q7 == "Carefully plan and organize before starting" else 0

    sensing_score += 1 if q8 == "Practical, immediate realities" else 0
    intuition_score += 1 if q8 == "Abstract possibilities and concepts" else 0

    # Determine Personality Type based on highest scores
    personality_type = ""
    personality_type += "I" if introvert_score > extrovert_score else "E"
    personality_type += "N" if intuition_score > sensing_score else "S"
    personality_type += "T" if thinking_score > feeling_score else "F"
    personality_type += "J" if judging_score > perceiving_score else "P"

    st.write(f"Based on your answers, we identified your personality type as **{personality_type}**.")

    # Step 3: Format Course Information
    json_file_path = "courses_info.json"
    json_data = load_json(json_file_path)

    def format_json_for_gemini(data):
        formatted_text = "Here is the detailed course information:\n\n"
        for item in data:
            course_summary = f"Course: {item.get('Course')}\n"
            course_summary += f"Degree: {item.get('Degree')}\n"
            course_summary += f"Semesters: {item.get('Semester')}\n"
            course_summary += f"Duration (Years): {item.get('Duration(Year)')}\n"
            course_summary += f"Course Fee (RM): {item.get('Course Fee(RM)')}\n"
            course_summary += f"Min Entry Requirement: {item.get('Min Entry Requirement')}\n"
            course_summary += f"Career Prospects: {item.get('Career Prospects')}\n"
            
            modules = [f"{year_key}: {item.get(year_key)}" for year_key in ["Y1 module", "Y2 module", "Y3 module"] if item.get(year_key)]
            course_summary += "Modules:\n" + "\n".join(modules) + "\n\n"
            formatted_text += course_summary
        return formatted_text

    formatted_text = format_json_for_gemini(json_data)

    # Step 4: Generate Recommendations
    def generate_recommendations(personality, description):
        system_prompt = (
            "You are an experienced Academic Consultant for New Era University College, with a focus on providing expert academic guidance tailored to students' goals, strengths, and interests. "
            "You also incorporate MBTI personality insights into your recommendations to help students choose suitable courses. "
            "Provide information in smaller chunks to avoid overwhelming the user, and prompt them to ask for further details if needed.\n\n"
            
            f"User's personality type is {personality}. Based on this type, provide courses that align well with this personality.\n"
        )

        if description:
            system_prompt += f"\nUser's situation and goals:\n{description}\n\n"
        
        system_prompt += f"Course data:\n{formatted_text}"

        input_message = system_prompt
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_message)
        return response.text

    if st.button("Get Course Recommendations"):
        response = generate_recommendations(personality_type, user_description)
        st.subheader("Recommended Courses")
        st.markdown(response)

if __name__ == "__main__":
    main()
