"""
Pydantic models for configuration data.
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class RootDimensions(BaseModel):
    """Dimensions A, B, C, D for root characteristics"""
    A: Optional[float] = None
    B: Optional[float] = None
    C: Optional[float] = None
    D: Optional[float] = None


class LayoutDetails(BaseModel):
    """Layout measurements for planting configuration"""
    IF: Optional[float] = None  # Interfila
    IP: Optional[float] = None  # Interpianta
    IB: Optional[float] = None  # Interbina (only for twin rows)


class RaisedBedDetails(BaseModel):
    """Raised bed specifications"""
    AT: Optional[float] = None  # Altezza
    LT: Optional[float] = None  # Larghezza
    IT: Optional[float] = None  # Inter baula
    ST: Optional[float] = None  # Spazio tra baule


class MulchDetails(BaseModel):
    """Mulch specifications"""
    LP: Optional[float] = None  # Larghezza telo


class ConfigurationData(BaseModel):
    """Complete configuration collected through conversation"""
    conversation_id: UUID
    
    # Phase 1: Plant
    crop_type: Optional[str] = None
    root_type: Optional[str] = None
    root_dimensions: Optional[RootDimensions] = None
    
    # Phase 2: Layout
    row_type: Optional[str] = None  # Single/Twin
    layout_details: Optional[LayoutDetails] = None
    
    # Phase 3: Environment
    environment: Optional[str] = None
    is_raised_bed: Optional[bool] = None
    raised_bed_details: Optional[RaisedBedDetails] = None
    is_mulch: Optional[bool] = None
    mulch_details: Optional[MulchDetails] = None
    soil_type: Optional[str] = None
    
    # Phase 4: Tractor
    wheel_distance: Optional[float] = None
    tractor_hp: Optional[int] = None
    
    # Phase 5: Accessories
    accessories_primary: List[str] = []
    accessories_secondary: List[str] = []
    accessories_element: List[str] = []
    
    # Phase 6: Closing
    user_notes: Optional[str] = None
    is_interested: Optional[bool] = None
    contact_email: Optional[str] = None
    vat_number: Optional[str] = None
    
    is_complete: bool = False
