import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Load sections and modules
def load_sections_and_modules():
    try:
        df = pd.read_excel('questions.xlsx')
        sections = df.iloc[:, 7].unique()  # Column H (index 7)
        section_modules = {}
        for section in sections:
            if pd.isna(section):
                continue
            modules = df[df.iloc[:, 7] == section].iloc[:, 8].unique()
            section_modules[section] = [m for m in modules if not pd.isna(m)]
        return section_modules
    except Exception as e:
        st.error(f"Error loading sections and modules: {str(e)}")
        return {}

# Load questions for the selected section and module
def load_questions(selected_section, selected_module):
    try:
        df = pd.read_excel('questions.xlsx')
        module_df = df[(df.iloc[:, 7] == selected_section) & (df.iloc[:, 8] == selected_module)]
        questions = []
        for idx, row in module_df.iterrows():
            options = [str(row.iloc[i]) if not pd.isna(row.iloc[i]) else "" for i in range(1, 5)]
            options = [opt for opt in options if opt]
            correct_letter = str(row.iloc[5]).strip().lower() if not pd.isna(row.iloc[5]) else ""
            questions.append({
                'question': row.iloc[0],
                'options': options,
                'correct_letter': correct_letter,
                'correct_answer': options[ord(correct_letter) - ord('a')] if correct_letter else "",
                'description': row.iloc[6] if not pd.isna(row.iloc[6]) else ""
            })
        return questions
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# Initialize session state variables
def initialize_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'exam_submitted' not in st.session_state:
        st.session_state.exam_submitted = False
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = None
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

# Show Home Page with Section and Module selection
def show_home_page():
    st.title("Salesforce AI Associate Exam Dump")
    st.markdown("---")
    section_modules = load_sections_and_modules()
    
    if not section_modules:
        st.error("No sections found in the Excel file.")
        return
    
    st.markdown(
        """
        <style>
        h1 {
            font-size: 10px;
            color: purple;
            font-weight: bold;
            font-family: Arial, sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<h3>Select Exam Section</h3>', unsafe_allow_html=True)

    columns = st.columns(3)
    for idx, section in enumerate(section_modules.keys()):
        with columns[idx % 3]:
            if st.button(section, key=f"section_{section}", use_container_width=True):
                st.session_state.selected_section = section
                st.session_state.selected_module = None
                st.session_state.exam_started = False
                st.rerun()

    # Module Selection
    if st.session_state.selected_section:
        st.header(f"Select Module for {st.session_state.selected_section}")
        columns = st.columns(3)
        for idx, module in enumerate(section_modules[st.session_state.selected_section]):
            with columns[idx % 3]:
                if st.button(module, key=f"module_{module}", use_container_width=True):
                    st.session_state.selected_module = module
                    st.session_state.exam_started = False
                    st.rerun()

        if st.session_state.selected_module:
            st.markdown("---")
            st.markdown("### Module Information")
            st.markdown(f"**Selected Section:** {st.session_state.selected_section}")
            st.markdown(f"**Selected Module:** {st.session_state.selected_module}")

            questions = load_questions(st.session_state.selected_section, st.session_state.selected_module)
            if questions:
                st.markdown(f"**Total Questions:** {len(questions)}")
                if st.button("Start Exam", use_container_width=True):
                    st.session_state.exam_started = True
                    st.session_state.start_time = datetime.now()
                    st.rerun()
            else:
                st.error("No questions found for this module.")

def calculate_score(questions):
    correct = 0
    total = len(questions)
    for i, q in enumerate(questions):
        if i in st.session_state.user_answers:
            user_ans = st.session_state.user_answers[i]
            if user_ans.startswith(q['correct_letter'].lower()):
                correct += 1
    return correct, total

def is_answer_correct(question, user_answer):
    if user_answer is None:
        return False
    return user_answer.startswith(question['correct_letter'].lower())


# Main Function to display the exam and results
def main():
    st.set_page_config(page_title="Professional Exam Portal", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
        .stButton button { width: 100%; }
        .question-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .review-header-correct { background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin: 5px 0; }
        .review-header-incorrect { background-color: #ffebee; padding: 10px; border-radius: 5px; margin: 5px 0; }
    </style>""", unsafe_allow_html=True)

    initialize_session_state()

    if not st.session_state.exam_started:
        show_home_page()
        return

    # Load questions
    questions = load_questions(st.session_state.selected_section, st.session_state.selected_module)
    if not questions:
        st.error("No questions found.")
        return

    # Exam Interface
# In the exam interface part, where you display the questions:

    if not st.session_state.exam_submitted:
        st.title(f"Exam: {st.session_state.selected_section}")
        st.subheader(f"Module: {st.session_state.selected_module}")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 8, 2])
        with col1:
            if st.button("← Previous") and st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.rerun()
        
        with col3:
            if st.button("Next →") and st.session_state.current_question < len(questions) - 1:
                st.session_state.current_question += 1
                st.rerun()
    
        st.progress((st.session_state.current_question + 1) / len(questions))
        st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")
        
        current_q = questions[st.session_state.current_question]
        st.markdown(f"<div class='question-box'><h3>Question {st.session_state.current_question + 1}</h3><p>{current_q['question']}</p></div>", unsafe_allow_html=True)
    
        # Set the selected_answer to None to prevent default selection
        selected_answer = st.radio("Select your answer:", current_q['options'], key=f"q_{st.session_state.current_question}", index=None)
    
        if selected_answer:
            st.session_state.user_answers[st.session_state.current_question] = selected_answer

        st.markdown("---")
        cols = st.columns(len(questions))
        for i, col in enumerate(cols):
            button_style = "primary" if i == st.session_state.current_question else "secondary"
            answered_style = "✓" if i in st.session_state.user_answers else str(i + 1)
            if col.button(answered_style, key=f"nav_{i}", type=button_style):
                st.session_state.current_question = i
                st.rerun()

        # Exit and Submit Buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Exit Exam"):
                st.session_state.clear()
                st.rerun()

        with col2:
            if st.button("Submit Exam"):
                if len(st.session_state.user_answers) < len(questions):
                    st.warning("Please answer all questions before submitting.")
                else:
                    st.session_state.exam_submitted = True
                    st.rerun()

    else:
        # Show results
        st.title("Exam Results")
        st.subheader(f"Section: {st.session_state.selected_section}")
        st.subheader(f"Module: {st.session_state.selected_module}")
        st.markdown("---")
        
        correct, total = calculate_score(questions)
        percentage = (correct / total) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Questions", total)
        with col2:
            st.metric("Correct Answers", correct)
        with col3:
            st.metric("Score", f"{percentage:.1f}%")

        st.markdown("### Review Answers")
        for i, question in enumerate(questions):
            user_answer = st.session_state.user_answers.get(i)
            
            is_correct = is_answer_correct(question, user_answer)
            status_color = "correct" if is_correct else "incorrect"
            st.markdown(f"<div class='review-header-{status_color}'>Question {i + 1}: {'✓ Correct' if is_correct else '✗ Incorrect'}</div>", unsafe_allow_html=True)
            
            with st.expander(f"View Details"):
                st.write("**Question:**", question['question'])
                st.write("**Options:**")
                for idx, option in enumerate(question['options']):
                    if idx == (ord(question['correct_letter']) - ord('a')):
                        st.success(f"{option} ✓")
                    elif user_answer == option:
                        st.error(f"{option} ✗")
                    else:
                        st.write(option)
                st.write("**Your Answer:**", user_answer or "Not answered")
                st.write("**Correct Answer:**", question['correct_answer'])
                if question['description']:
                    st.write("**Explanation:**", question['description'])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Return to Home"):
                st.session_state.clear()
                st.rerun()
        with col2:
            if st.button("Start New Exam"):
                st.session_state.exam_submitted = False
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()
