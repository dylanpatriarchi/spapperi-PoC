from .state import AgentState
from .logic import get_next_missing_field, QUESTIONS
from langchain_core.messages import AIMessage, HumanMessage

def node_analyst(state: AgentState):
    """
    Analyzes the LAST user message and updates the configuration.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"user_config": state.get("user_config", {})}
    
    last_message = messages[-1]
    current_config = state.get("user_config", {})
    
    # Retrieve what field we were waiting for (if stored in state, user session, or inferred)
    # For this stateless POC, we re-calculate missing field of the *previous* state 
    # OR we rely on 'next_step' passed in the thread config (feature of LangGraph checkpointer).
    # SIMPLIFICATION: We assume the backend passes 'next_step' in the inputs or we deduce it.
    
    # DYNAMIC LOGIC:
    # 1. Identify what we were asking.
    target_field = state.get("next_step") # This needs to be persisted
    
    updates = {}
    if target_field and target_field != "complete":
        from .chain import extractor_chain
        
        print(f"--- Analyst: Extracting '{last_message.content}' for field '{target_field}' ---")
        try:
            extraction = extractor_chain.invoke({
                "field_name": target_field,
                "config": current_config,
                "input": last_message.content
            })
            
            value = extraction.get("value")
            if value is not None:
                updates[target_field] = value
                print(f"--- Analyst: Extracted Value: {value} ---")
            else:
                 print(f"--- Analyst: Could not extract value for {target_field} ---")
                 # Logic to ask again or clarify could go here
                 
        except Exception as e:
            print(f"--- Extraction Error: {e} ---")
            # Fallback (maintain state)

        # Merge updates into config
        new_config = {**current_config, **updates}
        return {"user_config": new_config}
    
    return state


def node_manager(state: AgentState):
    """
    Determines the next step based on the config.
    """
    config = state.get("user_config") or {}
    next_field = get_next_missing_field(config)
    
    print(f"--- Manager Node: Next Field is {next_field} ---")
    
    technical_question_template = QUESTIONS.get(next_field, "Configurazione Completata! Genero il PDF...")
    
    # Generate Natural Response using LLM
    from .chain import generation_chain
    last_user_msg = state["messages"][-1].content if state.get("messages") else "Start"
    
    try:
        natural_question = generation_chain.invoke({
            "last_user_message": last_user_msg,
            "config": config,
            "technical_question": technical_question_template
        })
    except Exception:
        natural_question = technical_question_template # Fallback

    return {
        "next_step": next_field,
        "messages": [AIMessage(content=natural_question)]
    }
