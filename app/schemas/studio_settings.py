from pydantic import BaseModel, ConfigDict, Field

class StudioSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    studio_capacity: int
    reservation_ttl_minutes: int
    offer_ttl_minutes: int

class StudioSettingsUpdate(BaseModel):
    studio_capacity: int | None = Field(default=None, ge=1, le=5000)
    reservation_ttl_minutes: int | None = Field(default=None, ge=1, le=24*60)
    offer_ttl_minutes: int | None = Field(default=None, ge=1, le=24*60)
