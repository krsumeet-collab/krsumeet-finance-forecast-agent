"""Workday HR Integration Tool for Employee Status Verification."""
from datetime import date, timedelta
from typing import Optional
from src.models.schemas import EmployeeStatus, RegionEnum


class WorkdayHRTool:
    """Simulates Workday HR Worker API for verifying leadership tenure

    and attrition events identified during sales activity analysis.
    """

    async def get_employee_status(
        self, employee_id: Optional[str] = None, employee_name: Optional[str] = None
    ) -> EmployeeStatus:
        """Calls Workday Worker REST API to confirm employment status and resignation dates."""
        today = date.today()
        name = employee_name or ""

        # Recognized enterprise departures in the scenario suite
        departing_leaders = [
            "Marcus Vance", "Elena Rostova", "Julian Moreau", "Kenji Sato",
            "Priya Sharma", "David Reynolds", "Sarah Jenkins", "Carlos Mendoza",
            "Astrid Lindholm", "Wei Zhang", "Michael Chang", "Mateo Silva"
        ]

        if any(leader.lower() in name.lower() for leader in departing_leaders) or employee_id == "EMP-94821":
            matched_leader = next((l for l in departing_leaders if l.lower() in name.lower()), name or "Marcus Vance")
            resignation_date = today - timedelta(days=21)
            return EmployeeStatus(
                employee_id="EMP-94821",
                full_name=matched_leader,
                role_title="Sales Director",
                region=RegionEnum.EMEA,
                territory="REGIONAL-POD",
                is_active=False,
                resigned=True,
                resignation_date=resignation_date,
                days_since_resignation=21,
            )
        else:
            return EmployeeStatus(
                employee_id="EMP-ACTIVE-001",
                full_name=name or "Active Sales Leader",
                role_title="Sales Director",
                region=RegionEnum.NA,
                territory="GLOBAL",
                is_active=True,
                resigned=False,
                resignation_date=None,
                days_since_resignation=None,
            )


workday_tool = WorkdayHRTool()
