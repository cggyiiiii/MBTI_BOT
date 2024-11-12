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

    st.title("NEUC Academic Consultant")
    st.text(
        "**To help me create the best solution for you, please share a bit about yourself! You might include:**\n\n"
        "What are your main concerns or challenges right now?\n"
        "What are your career aspirations or future goals?\n"
        "Any specific interests or areas where you'd like support?\n\n"
        "This information will help me provide a tailored and effective solution for your needs!"
    )

    # Function to format JSON data for output
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

    json_file_path = "courses_info.json"
    json_data = load_json(json_file_path)
    formatted_text = format_json_for_gemini(json_data)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I’m here to help you with your academic choices. Feel free to tell me a bit about your interests or ask for course recommendations."
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def generate_recommendations(query):
        system_prompt = (
            "You are an experienced Academic Consultant for New Era University College, with a focus on providing expert academic guidance tailored to students' goals, strengths, and interests. "
            "Your primary role is to offer clear, practical advice to help students make informed decisions about their academic paths, whether they need information on specific courses, career prospects, or academic requirements. "
            "Provide information in smaller chunks to avoid overwhelming the user, and prompt them to ask for further details if needed.\n\n"
            
            "When applicable and helpful, you can use insights from MBTI to enhance recommendations, but focus first on addressing the user’s specific academic questions. "
            "If MBTI is not mentioned by the user or isn't directly relevant to their academic choices, do not provide MBTI-related insights. "
            "If MBTI is relevant to their choices, mention briefly how certain personality traits may align with specific academic settings or learning styles "
            "(e.g., Introverts (I) may benefit from quieter, independent study environments, while Extraverts (E) might excel in collaborative learning).\n\n"
            
            "In every response, prioritize direct, actionable guidance on the user’s academic questions. If the user provides abbreviations (e.g., 'CS' for Computer Science or 'TCSL' for Teaching Chinese as Second Language), recognize and expand them into their full form, making sure the information remains relevant. "
            "Provide well-rounded suggestions that encourage the user to consider additional factors beyond personality for a comprehensive decision-making process. "
            "If a user is directly seeking MBTI-based insights, provide thoughtful explanations about how MBTI traits might align with their academic preferences and study environments. "
            "Otherwise, deliver straightforward academic guidance that builds confidence in their academic choices."
        )


        input_message = f"{system_prompt}\n\nUser query: {query}\n\nCourse data:\n{formatted_text}"

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_message)
        return response.text

    def llm_function(query):
        response = generate_recommendations(query)
        
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": response})

    query = st.chat_input("Please give some description about yourself")
    
    if query:
        with st.chat_message("user"):
            st.markdown(query)
        llm_function(query)

if __name__ == "__main__":
    main()
