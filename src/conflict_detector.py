"""Conflict detection for drone operations."""
from typing import List
from datetime import datetime
from models import Pilot, Drone, Mission, Conflict

class ConflictDetector:
    """Detects conflicts and issues in drone operations."""
    
    def __init__(self, database):
        self.db = database
        self.conflicts: List[Conflict] = []
    
    def detect_all_conflicts(self) -> List[Conflict]:
        """Detect all conflicts in current state."""
        self.conflicts = []
        
        # Check for scheduling conflicts
        for mission_id, mission in self.db.missions.items():
            if mission.assigned_pilot:
                self._check_double_booking(mission.assigned_pilot, mission)
            if mission.assigned_drone:
                self._check_drone_double_booking(mission.assigned_drone, mission)
                self._check_maintenance_conflict(mission.assigned_drone, mission)
        
        # Check for skill/cert mismatches
        for mission_id, mission in self.db.missions.items():
            if mission.assigned_pilot:
                self._check_skill_mismatch(mission.assigned_pilot, mission)
                self._check_cert_mismatch(mission.assigned_pilot, mission)
        
        # Check for location mismatches
        for mission_id, mission in self.db.missions.items():
            if mission.assigned_pilot and mission.assigned_drone:
                self._check_location_mismatch(mission)
        
        return self.conflicts
    
    def _check_double_booking(self, pilot_id: str, mission: Mission):
        """Check if pilot has overlapping assignments."""
        pilot = self.db.get_pilot_by_id(pilot_id)
        if not pilot or not pilot.current_assignment:
            return
        
        # Check if pilot is assigned to another mission with overlapping dates
        other_mission = self.db.get_mission_by_id(pilot.current_assignment)
        if other_mission and self._dates_overlap(mission.start_date, mission.end_date, 
                                                  other_mission.start_date, other_mission.end_date):
            self.conflicts.append(Conflict(
                conflict_type="double-booking",
                severity="critical",
                description=f"Pilot {pilot.name} is assigned to overlapping projects: {mission.project_id} and {other_mission.project_id}",
                affected_pilot=pilot_id,
                affected_mission=mission.project_id
            ))
    
    def _check_drone_double_booking(self, drone_id: str, mission: Mission):
        """Check if drone has overlapping assignments."""
        drone = self.db.get_drone_by_id(drone_id)
        if not drone or not drone.current_assignment:
            return
        
        other_mission = self.db.get_mission_by_id(drone.current_assignment)
        if other_mission and self._dates_overlap(mission.start_date, mission.end_date,
                                                  other_mission.start_date, other_mission.end_date):
            self.conflicts.append(Conflict(
                conflict_type="double-booking",
                severity="critical",
                description=f"Drone {drone.model} is assigned to overlapping projects: {mission.project_id} and {other_mission.project_id}",
                affected_drone=drone_id,
                affected_mission=mission.project_id
            ))
    
    def _check_maintenance_conflict(self, drone_id: str, mission: Mission):
        """Check if drone is in maintenance."""
        drone = self.db.get_drone_by_id(drone_id)
        if not drone or not drone.is_in_maintenance():
            return
        
        self.conflicts.append(Conflict(
            conflict_type="maintenance-conflict",
            severity="critical",
            description=f"Drone {drone.model} assigned to {mission.project_id} but is currently in maintenance",
            affected_drone=drone_id,
            affected_mission=mission.project_id
        ))
    
    def _check_skill_mismatch(self, pilot_id: str, mission: Mission):
        """Check if pilot has required skills."""
        pilot = self.db.get_pilot_by_id(pilot_id)
        if not pilot:
            return
        
        missing_skills = [s for s in mission.required_skills if s not in pilot.skills]
        if missing_skills:
            self.conflicts.append(Conflict(
                conflict_type="skill-mismatch",
                severity="major",
                description=f"Pilot {pilot.name} lacks required skills for {mission.project_id}: {', '.join(missing_skills)}",
                affected_pilot=pilot_id,
                affected_mission=mission.project_id
            ))
    
    def _check_cert_mismatch(self, pilot_id: str, mission: Mission):
        """Check if pilot has required certifications."""
        pilot = self.db.get_pilot_by_id(pilot_id)
        if not pilot:
            return
        
        missing_certs = [c for c in mission.required_certs if c not in pilot.certifications]
        if missing_certs:
            self.conflicts.append(Conflict(
                conflict_type="skill-mismatch",
                severity="critical",
                description=f"Pilot {pilot.name} lacks required certifications for {mission.project_id}: {', '.join(missing_certs)}",
                affected_pilot=pilot_id,
                affected_mission=mission.project_id
            ))
    
    def _check_location_mismatch(self, mission: Mission):
        """Check if pilot and drone are in same location."""
        pilot = self.db.get_pilot_by_id(mission.assigned_pilot)
        drone = self.db.get_drone_by_id(mission.assigned_drone)
        
        if pilot and drone and pilot.location != drone.location:
            self.conflicts.append(Conflict(
                conflict_type="location-mismatch",
                severity="major",
                description=f"Pilot {pilot.name} (in {pilot.location}) and drone {drone.model} (in {drone.location}) are in different locations for {mission.project_id}",
                affected_pilot=mission.assigned_pilot,
                affected_drone=mission.assigned_drone,
                affected_mission=mission.project_id
            ))
    
    @staticmethod
    def _dates_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
        """Check if two date ranges overlap."""
        return start1 < end2 and start2 < end1
