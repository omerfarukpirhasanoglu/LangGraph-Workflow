from typing import TypedDict, Optional

class ChromaState(TypedDict, total=False):
    # Chroma v1.2'den gelen veri
    image_ref: str
    model_output: dict
    
    # History'den gelen ve History'ye giden veri
    history_summary: str

    # LLM:Interpretation ile ilgili veri
    device_id: str 
    user_context: Optional[str]
    needs_clarification: bool
    clarification_asked: bool
    interpretation: str

    final_response: str