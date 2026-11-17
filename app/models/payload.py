from pydantic import BaseModel

class AudioRequest(BaseModel):
    input_path: str

class MetronomeResponse(BaseModel):
    output_path: str
    bpm: int
    tuning_hz: float
    musical_key: str