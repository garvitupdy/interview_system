import operator
from typing import TypedDict, Annotated, Dict
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


from agents import (
    run_intro_agent,
    run_question_agent,
    run_evaluation_agent,
    run_reporter_agent,
    EvaluationResult
)



class InterviewState(TypedDict):
    target_role: str

    chat_history: Annotated[list[BaseMessage], operator.add]
    current_round: str      
    question_count: int     
    current_question: str   
    current_answer: str     
    scores: Dict[str, int]  
    interviewer_feedback: str 
    
    accumulated_feedback: Annotated[str, operator.add] 
    status: str             




def intro_node(state: InterviewState) -> dict:
    """Initializes the interview and generates the welcome message."""
    target_role = state.get("target_role", "Software Engineer")
    welcome_msg = run_intro_agent(target_role)
    
    return {
        "chat_history": [AIMessage(content=welcome_msg)],
        "current_round": "Logical",
        "question_count": 0,
        "scores": {"Logical": 0, "Technical": 0, "HR": 0},
        "status": "ongoing",
        "interviewer_feedback": "",
        "accumulated_feedback": ""
    }


def question_node(state: InterviewState) -> dict:
    """
    Generates the next adaptive question and increments the count.
    Ensures the content stored in chat_history is a clean string.
    """
    
    raw_question = run_question_agent(
        target_role=state["target_role"],
        current_round=state["current_round"],
        interviewer_feedback=state.get("interviewer_feedback", ""),
        chat_history=state.get("chat_history", [])[-3:]
    )
    
    
    clean_question = str(raw_question)
    
    
    return {
        "current_question": clean_question,
        "chat_history": [AIMessage(content=clean_question)],
        "question_count": state.get("question_count", 0) + 1
    }




def evaluation_node(state: InterviewState) -> dict:
    """Evaluates the user's answer, updates scores, and handles round progression."""
   
    result: EvaluationResult = run_evaluation_agent(
        target_role=state["target_role"],
        current_round=state["current_round"],
        question=state["current_question"],
        answer=state["current_answer"]
    )
    
    current_round = state["current_round"]
    new_scores = state.get("scores", {"Logical": 0, "Technical": 0, "HR": 0})
    new_scores[current_round] += result.score
    
    status = state.get("status", "ongoing")
    next_round = current_round
    question_count = state["question_count"]
    
    
    if question_count == 5:
        if new_scores[current_round] < 30:
            status = "rejected"
        else:
           
            if current_round == "Logical":
                next_round = "Technical"
                question_count = 0
            elif current_round == "Technical":
                next_round = "HR"
                question_count = 0
            elif current_round == "HR":
                status = "passed"
                

    acc_feedback = (f"\nRound: {current_round} | Q: {state['current_question']} | "
                    f"Score: {result.score}/10 | Strengths: {result.strengths} | "
                    f"Weaknesses: {result.weaknesses}\n")
    
    return {
        "scores": new_scores,
        "interviewer_feedback": result.feedback_note,
        "accumulated_feedback": acc_feedback, 
        "status": status,
        "current_round": next_round,
        "question_count": question_count,

        "chat_history": [HumanMessage(content=state["current_answer"])]
    }

def reporter_node(state: InterviewState) -> dict:
    """Generates the final comprehensive interview report when rejected or completed."""
    final_report = run_reporter_agent(
        target_role=state["target_role"],
        final_status=state["status"],
        accumulated_feedback=state.get("accumulated_feedback", "")
    )
    
    return {
        "chat_history": [AIMessage(content=final_report)]
    }




def entry_router(state: InterviewState) -> str:
    """Decides where the graph starts when invoked."""
 
    if not state.get("chat_history"):
        return "intro_node"

    if state.get("status") in ["passed", "rejected"]:
        return END
    
    return "evaluation_node"

def route_after_evaluation(state: InterviewState) -> str:
    """Decides where to go after grading the answer."""
    if state.get("status") == "rejected" or state.get("status") == "passed":
        return "reporter_node"
        
    return "question_node"




def build_interview_graph():
    """Assembles and compiles the StateGraph."""
    builder = StateGraph(InterviewState)
    
    
    builder.add_node("intro_node", intro_node)
    builder.add_node("question_node", question_node)
    builder.add_node("evaluation_node", evaluation_node)
    builder.add_node("reporter_node", reporter_node)
    
    
    builder.set_conditional_entry_point(
        entry_router,
        {
            "intro_node": "intro_node",
            "evaluation_node": "evaluation_node",
            END: END
        }
    )
    
    
    builder.add_edge("intro_node", "question_node")
    
    
    builder.add_edge("question_node", END)
    
    builder.add_conditional_edges(
        "evaluation_node",
        route_after_evaluation,
        {
            "question_node": "question_node",
            "reporter_node": "reporter_node"
        }
    )
    
    builder.add_edge("reporter_node", END)
    
    return builder.compile()


app = build_interview_graph()