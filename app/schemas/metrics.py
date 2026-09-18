from datetime import datetime
from pydantic import BaseModel

class PrometheusHealthResponse(BaseModel):
    status: str
    url: str

class MetricValueResponse(BaseModel):
    server_id: int
    server_name: str
    instance: str
    metric: str
    value: float | None
    unit: str
    available: bool

class DiskUsageItem(BaseModel):
    volume: str
    used_percent: float

class DiskMetricsResponse(BaseModel):
    server_id: int
    server_name: str
    instance: str
    disks: list[DiskUsageItem]

class ServerMetricsOverviewResponse(BaseModel):
    server_id: int
    server_name: str
    instance: str
    cpu_percent: float | None
    memory_percent: float | None
    disks: list[DiskUsageItem]
    collected_at: datetime