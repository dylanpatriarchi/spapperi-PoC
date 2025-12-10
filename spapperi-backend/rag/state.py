from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class ConfigurationState(TypedDict):
    """
    Tracks the collected configuration data strictly adhering to flow.pdf.
    """
    # Phase 1
    crop_type: Optional[str]
    root_type: Optional[str]
    root_dimensions: Optional[dict] # {A, B, C, D}

    # Phase 2
    row_type: Optional[str] # Single / Twin
    layout_details: Optional[dict] # {IF, IP, IB}

    # Phase 3
    environment: Optional[str] # Open Field / Greenhouse
    is_raised_bed: Optional[bool]
    raised_bed_details: Optional[dict]
    is_mulch: Optional[bool]
    mulch_details: Optional[dict]
    soil_type: Optional[str]

    # Phase 4
    wheel_distance_internal: Optional[float]
    wheel_distance_external: Optional[float]
    tractor_hp: Optional[int]
    lift_category: Optional[str]
    has_auto_drive: Optional[bool]
    gps_model: Optional[str]

    # Phase 5
    accessories_primary: Optional[List[str]]
    accessories_secondary: Optional[List[str]]
    accessories_element: Optional[List[str]]

    # Phase 6
    user_notes: Optional[str]
    contact_email: Optional[str]
    vat_number: Optional[str]

class AgentState(TypedDict):
    """
    The Main Graph State.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    config: ConfigurationState
    current_phase: str # e.g., "phase_1_crop", "phase_2_layout"
    next_step: str # instruction for the LLM on what to ask next
