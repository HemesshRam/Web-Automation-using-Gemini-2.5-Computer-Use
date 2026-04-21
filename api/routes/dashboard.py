"""
Dashboard Routes — KPI Stats & Timeline Charts
"""

from fastapi import APIRouter
from api.services import DashboardService
from api.schemas import DashboardStats, TimelinePoint
from typing import List

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

dashboard_service = DashboardService()


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats():
    """Get aggregated KPI statistics for the dashboard"""
    return dashboard_service.get_stats()


@router.get("/timeline", response_model=List[TimelinePoint])
def get_timeline(days: int = 30):
    """Get execution performance timeline data for charts"""
    return dashboard_service.get_timeline(days=days)
