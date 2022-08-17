'''Schema for Tables'''
from datetime import datetime
from pydantic import BaseModel, Field


class QueueHeaderSchema(BaseModel):
    process_id: str = Field(None,title='Description of the process_id ', max_length = 32)
    process: str = Field(None,title='Process Type  ', max_length = 15)
    status: str = Field('new',title='Status of the Process  ', max_length = 10)
    created_time: datetime = Field(..., example="2022-07-01T00:00:00.000Z")

    class Config:
        orm_mode = True


class QueueDetailsSchema(BaseModel):
    input_json : dict
    class Config:
        orm_mode=True
