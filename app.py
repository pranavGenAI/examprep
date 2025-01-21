import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import random

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
                'description': row.iloc[6] if not pd.isna(row.iloc[6]) else "",
                'section': selected_section
            })
        return questions
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# Initialize session state variables
def initialize_session_state():
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'exam_submitted' not in st.session_state:
        st.session_state.exam_submitted = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'question_order' not in st.session_state:
        st.session_state.question_order = []
    if 'questions' not in st.session_state:
        st.session_state.questions = []

# Function to start the mockup exam
def start_mockup_exam():
    # Define section-wise question count
    section_question_count = {
        "AI Fundamentals": 7,
        "AI Capabilities in CRM": 3,
        "Data for AI": 14,
        "Ethical Considerations of AI": 16
    }
    
    # Load all questions for each section
    all_questions = []
    for section in section_question_count.keys():
        questions = load_questions(section, None)  # Get all questions for a section
        random.shuffle(questions)  # Shuffle questions for random order
        section_questions = questions[:section_question_count[section]]  # Limit to predefined count
        all_questions.extend(section_questions)  # Add to total list
    
    # Randomize the order of questions across sections
    random.shuffle(all_questions)
    st.session_state.questions = all_questions
    st.session_state.question_order = list(range(len(all_questions)))
    st.session_state.exam_started = True
    st.session_state.exam_submitted = False

# Function to calculate the score
def calculate_score():
    correct = 0
    total = len(st.session_state.questions)
    for i, q in enumerate(st.session_state.questions):
        if i in st.session_state.user_answers:
            user_ans = st.session_state.user_answers[i]
            if user_ans.startswith(q['correct_letter'].lower()):
                correct += 1
    return correct, total

# Main function to display the exam and results
def main():
    st.set_page_config(page_title="Professional Exam Portal", layout="wide")
    initialize_session_state()

    if not st.session_state.exam_started:
        st.title("Salesforce AI Associate Mock Exam")
        if st.button("Take Mockup Exam"):
            start_mockup_exam()
            st.rerun()
        return

    if st.session_state.exam_submitted:
        # Show results
        st.title("Exam Results")
        correct, total = calculate_score()
        percentage = (correct / total) * 100

        st.subheader(f"Total Questions: {total}")
        st.subheader(f"Correct Answers: {correct}")
        st.subheader(f"Score: {percentage:.1f}%")

        st.markdown("### Review Answers")
        for i, question in enumerate(st.session_state.questions):
            user_answer = st.session_state.user_answers.get(i)
            is_correct = user_answer and user_answer.startswith(question['correct_letter'].lower())
            color = 'green' if is_correct else 'red'
            
            st.markdown(f"<p style='color:{color};'>{question['section']} - Question {i + 1}: {user_answer or 'No answer'}</p>", unsafe_allow_html=True)
            st.write("**Question:**", question['question'])
            st.write("**Options:**")
            for idx, option in enumerate(question['options']):
                st.write(option)
            st.write("**Correct Answer:**", question['correct_answer'])
            if question['description']:
                st.write("**Explanation:**", question['description'])

        if st.button("Start New Exam"):
            st.session_state.clear()
            st.rerun()
        return

    # Exam Interface
    st.title("Mock Exam in Progress")
    st.subheader("Answer the following questions:")
    
    # Display the current question
    question_idx = st.session_state.question_order[0]
    question = st.session_state.questions[question_idx]

    st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px;'><h3>{question['section']}</h3><p>{question['question']}</p></div>", unsafe_allow_html=True)
    
    selected_answer = st.radio("Select your answer:", question['options'], key=f"q_{question_idx}")
    if selected_answer:
        st.session_state.user_answers[question_idx] = selected_answer
    
    # Navigation buttons
    if st.button("Next Question"):
        st.session_state.question_order.pop(0)  # Move to next question
        if st.session_state.question_order:
            st.rerun()
        else:
            st.session_state.exam_submitted = True
            st.rerun()

if __name__ == "__main__":
    main()
