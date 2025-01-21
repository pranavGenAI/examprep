import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

def get_option_by_letter(options, letter):
    """Get the option text corresponding to a letter (a,b,c,d)."""
    if not letter or pd.isna(letter):
        return ""
    letter = str(letter).strip().lower()
    idx = ord(letter) - ord('a')
    if 0 <= idx < len(options):
        return options[idx]
    return ""

def get_letter_from_option(options, selected_option):
    """Get the letter (a,b,c,d) corresponding to an option."""
    for idx, option in enumerate(options):
        if option == selected_option:
            return chr(ord('a') + idx)
    return ""

def load_questions():
    """Load questions from Excel file."""
    try:
        df = pd.read_excel('questions.xlsx')
        
        if len(df.columns) < 7:
            st.error("Excel file must have at least 7 columns")
            return []
            
        questions = []
        for idx, row in df.iterrows():
            # Get options, removing any NaN values
            options = [
                str(row.iloc[1]) if not pd.isna(row.iloc[1]) else "",
                str(row.iloc[2]) if not pd.isna(row.iloc[2]) else "",
                str(row.iloc[3]) if not pd.isna(row.iloc[3]) else "",
                str(row.iloc[4]) if not pd.isna(row.iloc[4]) else ""
            ]
            options = [opt for opt in options if opt]
            
            # Get correct answer letter (a,b,c,d)
            correct_letter = str(row.iloc[5]).strip().lower() if not pd.isna(row.iloc[5]) else ""
            
            questions.append({
                'question': row.iloc[0],
                'options': options,
                'correct_letter': correct_letter,
                'correct_answer': get_option_by_letter(options, correct_letter),
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
            user_ans = st.session_state.user_answers[i]
            if user_ans.startswith(q['correct_letter'] + ')'):
                correct += 1
    return correct, total

def is_answer_correct(question, user_answer):
    """Check if the user's answer is correct."""
    if user_answer is None:
        return False
    return user_answer.startswith(question['correct_letter'] + ')')

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
            
            options = [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(current_q['options'])]
            selected_answer = st.radio(
                "Select your answer:",
               # options,
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
                    if idx == (ord(question['correct_letter']) - ord('a')):
                        st.success(f"{full_option} ✓")
                    elif user_answer == full_option:
                        st.error(f"{full_option} ✗")
                    else:
                        st.write(full_option)
                
                st.write("**Your Answer:**", user_answer or "Not answered")
                correct_option = get_option_by_letter(question['options'], question['correct_letter'])
                st.write("**Correct Answer:**", f"{question['correct_letter'].upper()}) {correct_option}")
                if question['description']:
                    st.write("**Explanation:**", question['description'])
        
        if st.button("Start New Exam"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
