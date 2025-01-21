import streamlit as st
import pandas as pd
from datetime import datetime

def load_questions():
    """Load questions from Excel file."""
    try:
        # Read Excel file - now using column indices instead of letter names
        df = pd.read_excel('questions.xlsx')
        
        # Verify the dataframe has enough columns
        if len(df.columns) < 7:
            st.error("Excel file must have at least 7 columns (Question, 4 Options, Answer, and Description)")
            return []
            
        questions = []
        for idx, row in df.iterrows():
            questions.append({
                'question': row.iloc[0],  # First column (Question)
                'options': [
                    row.iloc[1],  # Second column (Option 1)
                    row.iloc[2],  # Third column (Option 2)
                    row.iloc[3],  # Fourth column (Option 3)
                    row.iloc[4]   # Fifth column (Option 4)
                ],
                'correct_answer': row.iloc[5],  # Sixth column (Correct Answer)
                'description': row.iloc[6]  # Seventh column (Description)
            })
        return questions
    except FileNotFoundError:
        st.error("Could not find 'questions.xlsx'. Please ensure the file exists in the same directory.")
        return []
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}\nPlease check your Excel file format.")
        return []

def initialize_session_state():
    """Initialize session state variables."""
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'exam_submitted' not in st.session_state:
        st.session_state.exam_submitted = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = datetime.now()

def calculate_score(questions):
    """Calculate the final score."""
    correct = 0
    total = len(questions)
    for i, q in enumerate(questions):
        if i in st.session_state.user_answers:
            if st.session_state.user_answers[i] == q['correct_answer']:
                correct += 1
    return correct, total

def main():
    st.set_page_config(page_title="Professional Exam Portal", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stButton button {
            width: 100%;
        }
        .question-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .option-text {
            margin-left: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Load questions
    questions = load_questions()
    
    if not questions:
        st.error("""
        No questions found. Please check your Excel file format:
        - Column 1: Question
        - Column 2: Option 1
        - Column 3: Option 2
        - Column 4: Option 3
        - Column 5: Option 4
        - Column 6: Correct Answer
        - Column 7: Description
        """)
        return
    
    # Header
    st.title("Professional Exam Portal")
    st.markdown("---")
    
    if not st.session_state.exam_submitted:
        # Question navigation
        col1, col2, col3 = st.columns([2,8,2])
        with col1:
            if st.button("← Previous") and st.session_state.current_question > 0:
                st.session_state.current_question -= 1
                st.rerun()
        
        with col3:
            if st.button("Next →") and st.session_state.current_question < len(questions) - 1:
                st.session_state.current_question += 1
                st.rerun()
        
        # Question progress
        st.progress((st.session_state.current_question + 1) / len(questions))
        st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")
        
        # Display current question
        current_q = questions[st.session_state.current_question]
        with st.container():
            st.markdown(f"""
                <div class="question-box">
                    <h3>Question {st.session_state.current_question + 1}</h3>
                    <p>{current_q['question']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Radio button for options
            selected_answer = st.radio(
                "Select your answer:",
                current_q['options'],
                key=f"q_{st.session_state.current_question}",
                index=None
            )
            
            if selected_answer:
                st.session_state.user_answers[st.session_state.current_question] = selected_answer
        
        # Question navigation buttons
        st.markdown("---")
        cols = st.columns(len(questions))
        for i, col in enumerate(cols):
            button_style = "primary" if i == st.session_state.current_question else "secondary"
            answered_style = "✓" if i in st.session_state.user_answers else str(i + 1)
            if col.button(answered_style, key=f"nav_{i}", type=button_style):
                st.session_state.current_question = i
                st.rerun()
        
        # Submit button
        st.markdown("---")
        if st.button("Submit Exam", type="primary"):
            if len(st.session_state.user_answers) < len(questions):
                st.warning("Please answer all questions before submitting.")
            else:
                st.session_state.exam_submitted = True
                st.rerun()
    
    else:
        # Display results
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
        
        # Review answers
        st.markdown("### Review Answers")
        for i, question in enumerate(questions):
            with st.expander(f"Question {i + 1}"):
                st.write("**Question:**", question['question'])
                st.write("**Options:**")
                for idx, option in enumerate(question['options']):
                    if option == question['correct_answer']:
                        st.success(f"{chr(65 + idx)}. {option} ✓")
                    elif option == st.session_state.user_answers.get(i):
                        st.error(f"{chr(65 + idx)}. {option} ✗")
                    else:
                        st.write(f"{chr(65 + idx)}. {option}")
                
                st.write("**Your Answer:**", st.session_state.user_answers.get(i, "Not answered"))
                st.write("**Correct Answer:**", question['correct_answer'])
                if st.session_state.user_answers.get(i) == question['correct_answer']:
                    st.success("Correct!")
                else:
                    st.error("Incorrect")
                st.write("**Explanation:**", question['description'])
        
        # Restart button
        if st.button("Start New Exam"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
