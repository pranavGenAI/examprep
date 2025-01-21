import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def clean_answer(answer):
    """Clean the answer string to handle different formats."""
    if pd.isna(answer):
        return ""
    # Remove letter prefix and clean up
    answer = str(answer).strip()
    if answer.lower().startswith(('a)', 'b)', 'c)', 'd)')):
        answer = answer[2:].strip()
    elif answer.lower() in ['a', 'b', 'c', 'd']:
        # Map single letter to corresponding option
        return f"Option {answer.upper()}"
    return answer

def load_questions():
    """Load questions from Excel file."""
    try:
        df = pd.read_excel('questions.xlsx')
        
        if len(df.columns) < 7:
            st.error("Excel file must have at least 7 columns")
            return []
            
        questions = []
        for idx, row in df.iterrows():
            # Clean and prepare options
            options = [
                clean_answer(row.iloc[1]),  # Option A
                clean_answer(row.iloc[2]),  # Option B
                clean_answer(row.iloc[3]),  # Option C
                clean_answer(row.iloc[4])   # Option D
            ]
            
            # Remove empty options
            options = [opt for opt in options if opt and not pd.isna(opt)]
            
            correct_answer = clean_answer(row.iloc[5])
            
            # If correct answer is a single letter, map it to the corresponding option
            if correct_answer.upper() in ['A', 'B', 'C', 'D']:
                correct_idx = ord(correct_answer.upper()) - ord('A')
                if correct_idx < len(options):
                    correct_answer = options[correct_idx]
            
            questions.append({
                'question': row.iloc[0],
                'options': options,
                'correct_answer': correct_answer,
                'description': row.iloc[6] if not pd.isna(row.iloc[6]) else ""
            })
        return questions
    except FileNotFoundError:
        st.error("Could not find 'questions.xlsx'")
        return []
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

def initialize_session_state():
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'exam_submitted' not in st.session_state:
        st.session_state.exam_submitted = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()

def calculate_score(questions):
    correct = 0
    total = len(questions)
    for i, q in enumerate(questions):
        if i in st.session_state.user_answers:
            user_ans = clean_answer(st.session_state.user_answers[i])
            correct_ans = clean_answer(q['correct_answer'])
            if user_ans == correct_ans:
                correct += 1
    return correct, total

def is_answer_correct(question, user_answer):
    """Check if the user's answer is correct."""
    if user_answer is None:
        return False
    return clean_answer(user_answer) == clean_answer(question['correct_answer'])

def main():
    st.set_page_config(page_title="Professional Exam Portal", layout="wide")
    
    st.markdown("""
        <style>
        .main { padding: 2rem; }
        .stButton button { width: 100%; }
        .question-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .correct-answer { color: #00c853; }
        .incorrect-answer { color: #ff1744; }
        .review-header-correct {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        .review-header-incorrect {
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    questions = load_questions()
    
    if not questions:
        st.error("No questions found. Please check your Excel file format.")
        return
    
    st.title("Professional Exam Portal")
    st.markdown("---")
    
    if not st.session_state.exam_submitted:
        col1, col2, col3 = st.columns([2,8,2])
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
        with st.container():
            st.markdown(f"""
                <div class="question-box">
                    <h3>Question {st.session_state.current_question + 1}</h3>
                    <p>{current_q['question']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            selected_answer = st.radio(
                "Select your answer:",
                [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(current_q['options'])],
                key=f"q_{st.session_state.current_question}",
                index=None
            )
            
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
        
        st.markdown("---")
        if st.button("Submit Exam", type="primary"):
            if len(st.session_state.user_answers) < len(questions):
                st.warning("Please answer all questions before submitting.")
            else:
                st.session_state.exam_submitted = True
                st.rerun()
    
    else:
        correct, total = calculate_score(questions)
        percentage = (correct / total) * 100
        
        st.header("Exam Results")
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
            
            # Show correct/incorrect status before expanding
            status_color = "correct" if is_correct else "incorrect"
            st.markdown(f"""
                <div class="review-header-{status_color}">
                    Question {i + 1}: {'✓ Correct' if is_correct else '✗ Incorrect'}
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View Details"):
                st.write("**Question:**", question['question'])
                st.write("**Options:**")
                for idx, option in enumerate(question['options']):
                    prefix = f"{chr(65 + idx)}) "
                    full_option = f"{prefix}{option}"
                    if clean_answer(option) == clean_answer(question['correct_answer']):
                        st.success(f"{full_option} ✓")
                    elif user_answer and full_option == user_answer:
                        st.error(f"{full_option} ✗")
                    else:
                        st.write(full_option)
                
                st.write("**Your Answer:**", user_answer or "Not answered")
                st.write("**Correct Answer:**", f"{question['correct_answer']}")
                if question['description']:
                    st.write("**Explanation:**", question['description'])
        
        if st.button("Start New Exam"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
