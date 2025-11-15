from pydantic import BaseModel


class TrainerRead(BaseModel):
    id: int
    full_name: str
    bio: str | None = None
    photo_url: str | None = None

    class Config:
        from_attributes = True
