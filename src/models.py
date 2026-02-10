"""Data models for Drone Operations Coordinator."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Pilot:
    """Pilot data model."""
    pilot_id: str
    name: str
    skills: List[str]
    certifications: List[str]
    location: str
    status: str  # Available, On Leave, Assigned, Unavailable
    current_assignment: Optional[str] = None
    available_from: Optional[datetime] = None
    
    def is_available(self, start_date: datetime, end_date: datetime) -> bool:
        """Check if pilot is available for a date range."""
        if self.status != "Available":
            return False
        if self.available_from and self.available_from > start_date:
            return False
        return True
    
    def has_skills(self, required_skills: List[str]) -> bool:
        """Check if pilot has all required skills."""
        return all(skill in self.skills for skill in required_skills)
    
    def has_certifications(self, required_certs: List[str]) -> bool:
        """Check if pilot has all required certifications."""
        return all(cert in self.certifications for cert in required_certs)


@dataclass
class Drone:
    """Drone data model."""
    drone_id: str
    model: str
    capabilities: List[str]
    status: str  # Available, Maintenance, Deployed
    location: str
    current_assignment: Optional[str] = None
    maintenance_due: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if drone is available for assignment."""
        return self.status == "Available"
    
    def has_capabilities(self, required_capabilities: List[str]) -> bool:
        """Check if drone has all required capabilities."""
        return all(cap in self.capabilities for cap in required_capabilities)
    
    def is_in_maintenance(self) -> bool:
        """Check if drone is in maintenance."""
        return self.status == "Maintenance"


@dataclass
class Mission:
    """Mission/Project data model."""
    project_id: str
    client: str
    location: str
    required_skills: List[str]
    required_certs: List[str]
    start_date: datetime
    end_date: datetime
    priority: str  # High, Urgent, Standard
    assigned_pilot: Optional[str] = None
    assigned_drone: Optional[str] = None
    
    def is_urgent(self) -> bool:
        """Check if mission is urgent."""
        return self.priority in ["Urgent", "High"]


@dataclass
class Conflict:
    """Represents a conflict or issue."""
    conflict_type: str  # double-booking, skill-mismatch, equipment-mismatch, location-mismatch, maintenance-conflict
    severity: str  # critical, major, minor
    description: str
    affected_pilot: Optional[str] = None
    affected_drone: Optional[str] = None
    affected_mission: Optional[str] = None
