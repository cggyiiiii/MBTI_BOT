import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import os
import pandas as pd
import altair as alt
from json_loader import load_json
import time
from streamlit_lottie import st_lottie
import requests
import plotly.express as px
import plotly.graph_objects as go

def load_lottie_url(url: str):
    """Load Lottie animation from URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def create_radar_chart(scores, personality_type):
    """Create an interactive radar chart for personality scores"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=personality_type
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3]
            )),
        showlegend=True,
        title=f"Personality Profile - Type {personality_type}"
    )
    return fig

def create_progress_animation():
    """Create a progress animation with custom styling"""
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    progress_bar.empty()

def main():
    # Page Configuration
    st.set_page_config(
        page_title="NEUC Academic Consultant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )





    load_dotenv()
    gen_key = os.getenv("GEMINI_API_KEY")

    if not gen_key:
        st.error("API key not found. Please set the GEMINI_API in the environment.")
        return

    genai.configure(api_key=gen_key)

    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Home", "Personality Assessment", "Course Recommendations"])
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "This AI-powered academic consultant helps you discover "
            "the perfect course based on your personality type and preferences."
        )

    if page == "Home":
        # Load and display Lottie animation
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
        lottie_json = load_lottie_url(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=300)

        st.title("🎓 Welcome to NEUC Academic Consultant")
        st.markdown("""
            ### Your Personal Guide to Academic Success
            
            Discover the perfect course that aligns with your personality and aspirations using our 
            AI-powered recommendation system. Our platform combines:
            
            - 🧠 Advanced personality assessment
            - 📊 Data-driven course matching
            - 🤖 AI-powered personalized recommendations
            - 📈 Interactive visualizations
            
            Get started by navigating to the Personality Assessment section!
        """)

    elif page == "Personality Assessment":
        st.title("Personality Assessment")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Tell us about yourself")
            user_description = st.text_area(
                "Describe your interests, goals, and aspirations:",
                placeholder="E.g., I'm passionate about technology and problem-solving...",
                height=150
            )

            st.subheader("Personality Questionnaire")
            with st.expander("📋 Answer these questions carefully", expanded=True):
                q1 = st.radio("1. Do you prefer:", ["Working independently", "Working in groups"])
                q2 = st.radio("2. Are you more:", ["Analytical and logical", "Empathetic and caring"])
                q3 = st.radio("3. When solving problems, do you prefer:", ["Structured plans", "Flexible approaches"])
                q4 = st.radio("4. Do you feel energized after social interactions?", ["Yes", "No"])
                q5 = st.radio("5. When making decisions, do you rely more on:", ["Facts", "Feelings"])
                q6 = st.radio("6. Do you prefer to:", ["Plan ahead", "Go with the flow"])
                q7 = st.radio("7. When starting a new project, do you:", ["Dive in", "Plan carefully"])
                q8 = st.radio("8. Do you focus on:", ["Practical realities", "Abstract possibilities"])

        with col2:
            st.image("https://www.calmsage.com/wp-content/uploads/2022/08/what-are-the-myers-briggs-personality-types-1200x1251.jpg", 
                    caption="Different Personality Types")
            
            st.markdown("""
                ### Why Personality Matters
                Understanding your personality type can help you:
                - Choose courses that match your learning style
                - Identify potential career paths
                - Develop effective study strategies
                - Build on your natural strengths
            """)

        if st.button("Analyze My Personality", key="analyze"):
            create_progress_animation()
            
            # Scoring Logic
            scores = {
                'Introvert': (q1 == "Working independently") + (q4 == "No"),
                'Extrovert': (q1 == "Working in groups") + (q4 == "Yes"),
                'Thinking': (q2 == "Analytical and logical") + (q5 == "Facts"),
                'Feeling': (q2 == "Empathetic and caring") + (q5 == "Feelings"),
                'Judging': (q3 == "Structured plans") + (q6 == "Plan ahead") + (q7 == "Plan carefully"),
                'Perceiving': (q3 == "Flexible approaches") + (q6 == "Go with the flow") + (q7 == "Dive in"),
                'Sensing': (q8 == "Practical realities"),
                'Intuition': (q8 == "Abstract possibilities")
            }

            # Calculate personality type
            personality_type = (
                ("I" if scores['Introvert'] > scores['Extrovert'] else "E") +
                ("N" if scores['Intuition'] > scores['Sensing'] else "S") +
                ("T" if scores['Thinking'] > scores['Feeling'] else "F") +
                ("J" if scores['Judging'] > scores['Perceiving'] else "P")
            )

            st.session_state['personality_type'] = personality_type
            st.session_state['user_description'] = user_description
            
            # Display results in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"Your personality type is **{personality_type}**")
                radar_chart = create_radar_chart(scores, personality_type)
                st.plotly_chart(radar_chart, use_container_width=True)
            
            with col2:
                # Display personality traits explanation
                st.markdown(f"""
                    ### Your Personality Breakdown
                    
                    Your type **{personality_type}** indicates:
                    - {'Introvert (I): Prefers quiet reflection' if 'I' in personality_type else 'Extrovert (E): Enjoys social interaction'}
                    - {'Intuitive (N): Focuses on possibilities' if 'N' in personality_type else 'Sensing (S): Focuses on facts'}
                    - {'Thinking (T): Makes logical decisions' if 'T' in personality_type else 'Feeling (F): Makes value-based decisions'}
                    - {'Judging (J): Prefers structure' if 'J' in personality_type else 'Perceiving (P): Prefers flexibility'}
                """)

    elif page == "Course Recommendations":
        st.title("📚 Course Recommendations")
        
        if 'personality_type' not in st.session_state:
            st.warning("Please complete the personality assessment first!")
            return
            
        personality_type = st.session_state['personality_type']
        user_description = st.session_state.get('user_description', '')
        
        st.info(f"Generating personalized recommendations for personality type: **{personality_type}**")
        
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

        if st.button("Generate Recommendations", key="generate"):
            create_progress_animation()
            
            def generate_recommendations(personality, description):
                system_prompt = (
                    """You are an experienced Academic Consultant for New Era University College, focused on providing expert academic guidance based on students' goals, strengths, and interests. 
                    Your role is to offer clear, practical advice to support informed decisions about academic paths, career prospects, and course requirements.
                    If MBTI insights are relevant and helpful, briefly mention how certain personality traits might align with specific academic settings or learning styles (e.g., Introverts may prefer independent study environments, while Extraverts may excel in group settings). 
                    However, if MBTI is not relevant, focus only on the academic guidance requested.
                    Always provide direct, actionable advice tailored to the user's specific academic queries. 
                    Recognize and expand abbreviations (e.g., 'CS' as Computer Science) to maintain clarity. 
                    Offer well-rounded recommendations, encouraging the user to consider additional factors beyond personality for a thorough decision-making process.

                    You should only suggest no more than 4 courses to the user, because the user may feel overwhelmed by too many options. 
                    Ensure that the courses you recommend are relevant to the user's personality type and align with their academic interests and career goals. 
                    Include key details about each course, such as the degree offered, duration, minimum entry requirements, and potential career prospects. 
                    Encourage the user to explore these courses further to make an informed decision about their academic future.
                    """
                    f"User's personality type: {personality}\n"
                )
                if description:
                    system_prompt += f"User's situation and goals: {description}\n\n"
                system_prompt += f"Course data:\n{formatted_text}"

                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(system_prompt)
                return response.text

            response = generate_recommendations(personality_type, user_description)

            
            
            # Display recommendations in a nice format
            st.markdown("### 🎯 Your Personalized Recommendations")
            st.markdown(response)
            
            # Add option to download recommendations
            st.download_button(
                label="Download Recommendations",
                data=response,
                file_name="academic_recommendations.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()