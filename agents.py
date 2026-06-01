
import os
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_cohere import ChatCohere
from dotenv import load_dotenv

load_dotenv()


groq_llm_question = ChatGroq(
    model="llama-3.1-8b-instant", 
    temperature=0.7,
    groq_api_key = os.getenv('GROQ_API_KEY2')
)

groq_llm_evaluator = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.2,
    groq_api_key = os.getenv("GROQ_API_KEY")

)

cohere_llm = ChatCohere(
    model="command-a-reasoning-08-2025", 
    temperature=0.5,
    cohere_api_key = os.getenv("COHERE_API_KEY")
)



class EvaluationResult(BaseModel):
    """Schema for the background Evaluation Node to return strict JSON"""
    score: int = Field(
        description="A score from 1 to 10 based on the accuracy, logic, and clarity of the user's answer."
    )
    is_passing: bool = Field(
        description="True if the score is 6 or above, False otherwise."
    )
    feedback_note: str = Field(
        description="A brief internal note (1-2 sentences) explaining the score. This will be used to adapt the next question."
    )
    strengths: str = Field(
        description="What the candidate did well in this specific answer."
    )
    weaknesses: str = Field(
        description="Where the candidate failed or struggled in this specific answer."
    )



intro_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical interviewer. Welcome the candidate to their interview for the role of {target_role}.
    Briefly explain that this interview will consist of 3 rounds: Logical, Technical, and HR. 
    Keep the welcome warm, professional, and very brief (under 50 words). Do not ask a question yet.""")
])

question_generator_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert interviewer conducting a job interview.

Current Round: {current_round}
Target Role: {target_role}

Previous interviewer feedback:
{interviewer_feedback}

The chat history is provided only for limited context. The CURRENT ROUND always takes priority over any previous discussion.

ROUND DEFINITIONS

TECHNICAL ROUND:

* Ask questions that evaluate technical knowledge, tools, frameworks, architecture, coding concepts, debugging ability, design decisions, and role-specific expertise.
* Questions must be relevant to the role {target_role}.
* Do not ask HR or behavioral questions.

LOGICAL ROUND:

* Ask questions that evaluate reasoning, analytical thinking, problem solving, estimation, pattern recognition, decision making, or logic.
* Do not ask technical knowledge questions.
* Do not ask HR or behavioral questions.

HR ROUND:

* Ask behavioral and professional questions about communication, teamwork, leadership, conflict resolution, motivation, adaptability, career goals, work style, strengths, weaknesses, and workplace situations.
* Do not ask technical questions.
* Do not ask logical puzzle questions.

CRITICAL RULES

1. Ask exactly ONE question.

2. The question MUST belong to the CURRENT ROUND: {current_round}.

3. If the current round is different from topics discussed earlier in chat history, completely ignore those previous topics.

4. Never continue a topic from a previous round.

5. Use interviewer feedback only to adjust question depth:

   * If performance was strong, ask a more challenging question within the CURRENT ROUND.
   * If performance was weak, ask a simpler question within the CURRENT ROUND.

6. For Technical rounds, ensure the question is relevant to the role {target_role}.

7. For HR rounds, focus on behavior, communication, teamwork, leadership, motivation, career growth, conflict handling, and workplace situations.

8. For Logical rounds, focus on reasoning and problem solving rather than role-specific technical knowledge.

9. Do not provide answers.

10. Do not provide explanations.

11. Do not provide feedback.

12. Do not greet the candidate.

13. Do not mention the round name.

14. Do not number the question.

15. Output only the question text and nothing else.

Before responding, internally verify:

* Is the question valid for {current_round}?
* Is it appropriate for {target_role}?
* Is it exactly one question?
* Does it avoid topics from previous rounds?

If any answer is no, regenerate the question before responding.

    4. Only ask questions relevant to the {current_round} round.
    """),
    MessagesPlaceholder(variable_name="chat_history")
])

evaluation_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a strict, objective grader evaluating an interview for the role of {target_role} in the {current_round} round.
    
    Look at the Interviewer's Question and the Candidate's Answer below.
    Grade the candidate strictly on a scale of 1 to 10. 
    10 = Flawless, expert-level understanding.
    1  = Completely wrong or irrelevant.
    
    Output your evaluation exactly matching the requested JSON schema."""),
    ("human", "Question asked: {question}\nCandidate's Answer: {answer}")
])

reporter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Senior HR Director at a top tech company. 
    Write a highly professional, encouraging, and structured summary report based on the provided feedback."""),
    
    ("human", """The candidate has completed their interview for the role of {target_role}.
    
    Based on the accumulated feedback notes below, write the final report.
    Include:
    - Overall Summary of their performance.
    - Key Strengths (bullet points).
    - Areas for Improvement (bullet points).
    - Final Hiring Decision Status: {final_status} (Passed / Rejected).
    
    Accumulated Feedback:
    {accumulated_feedback}
    """)
])



def run_intro_agent(target_role: str) -> str:
    """Generates the welcome message."""
    chain = intro_prompt | groq_llm_evaluator
    response = chain.invoke({"target_role": target_role})
    return response.content

def run_question_agent(target_role: str, current_round: str, interviewer_feedback: str, chat_history: list) -> str:
    """Generates the next adaptive question based on chat history and past performance."""
    chain = question_generator_prompt | groq_llm_question
    
    feedback = interviewer_feedback if interviewer_feedback else "No feedback yet. This is the first question of the round."
    
    response = chain.invoke({
        "target_role": target_role,
        "current_round": current_round,
        "interviewer_feedback": feedback,
        "chat_history": chat_history
    })
    content = response.content

    if isinstance(content, list):
        
        clean_text = "".join(block.get("text", "") for block in content if isinstance(block, dict))
        return clean_text
    
    
    return str(content)

def run_evaluation_agent(target_role: str, current_round: str, question: str, answer: str) -> EvaluationResult:
    """Evaluates the user's answer and returns a structured Pydantic object."""
    chain = evaluation_prompt | groq_llm_evaluator.with_structured_output(EvaluationResult)
    response = chain.invoke({
        "target_role": target_role,
        "current_round": current_round,
        "question": question,
        "answer": answer
    })
    return response

def run_reporter_agent(target_role: str, final_status: str, accumulated_feedback: str) -> str:
    """Generates the final comprehensive interview report."""
    chain = reporter_prompt | cohere_llm
    response = chain.invoke({
        "target_role": target_role,
        "final_status": final_status,
        "accumulated_feedback": accumulated_feedback
    })
    content = response.content

    if isinstance(content, list):
        
        clean_text = "".join(block.get("text", "") for block in content if isinstance(block, dict))
        return clean_text


