from pydantic import BaseModel, Field


class ExperimentConfig(BaseModel):
    dataset: str = Field(..., description="vrplib|solomon|homberger")
    instance: str
    time_limit_s: int = 10
    population_size: int = 100


class StopRequest(BaseModel):
    run_id: str
