from pydantic import BaseModel


class GraphStatsResponse(BaseModel):
    total_rfps: int
    open_rfps: int
    total_organizations: int
    total_locations: int
    total_categories: int
    total_requirements: int
    total_relationships: int
