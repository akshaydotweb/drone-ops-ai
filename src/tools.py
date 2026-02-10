"""Tools for the Drone Operations Agent."""
import json
from typing import Optional, List
from database import DroneDatabase
from conflict_detector import ConflictDetector

class DroneOperationsTools:
    """Tools available to the agent."""
    
    def __init__(self, db: DroneDatabase):
        self.db = db
        self.conflict_detector = ConflictDetector(db)
    
    # ===== PILOT TOOLS =====
    def find_available_pilots(self, location: Optional[str] = None, skill: Optional[str] = None) -> str:
        """Find available pilots, optionally filtered by location and/or skill."""
        pilots = self.db.get_available_pilots(location=location, skill=skill)
        
        if not pilots:
            return "No available pilots found matching criteria."
        
        result = f"Available Pilots ({len(pilots)}):\n\n"
        for i, pilot in enumerate(pilots, 1):
            result += f"{i}. {pilot.name} ({pilot.pilot_id})\n"
            result += f"   Skills: {', '.join(pilot.skills)}\n"
            result += f"   Certifications: {', '.join(pilot.certifications)}\n"
            result += f"   Location: {pilot.location}\n"
            result += f"   Status: {pilot.status}\n\n"
        
        return result
    
    def get_pilot_details(self, pilot_id: str) -> str:
        """Get detailed information about a specific pilot."""
        pilot = self.db.get_pilot_by_id(pilot_id)
        if not pilot:
            return f"Pilot {pilot_id} not found."
        
        result = f"Pilot Details: {pilot.name}\n\n"
        result += f"ID: {pilot.pilot_id}\n"
        result += f"Location: {pilot.location}\n"
        result += f"Status: {pilot.status}\n\n"
        result += f"Skills: {', '.join(pilot.skills)}\n"
        result += f"Certifications: {', '.join(pilot.certifications)}\n\n"
        result += f"Current Assignment: {pilot.current_assignment or 'None'}\n"
        result += f"Available From: {pilot.available_from or 'Available now'}\n"
        return result
    
    def get_pilot_availability(self, pilot_id: str, start_date: str, end_date: str) -> str:
        """Check if a pilot is available for a date range."""
        from datetime import datetime
        pilot = self.db.get_pilot_by_id(pilot_id)
        if not pilot:
            return f"Pilot {pilot_id} not found."
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            is_available = pilot.is_available(start, end)
            return f"Pilot {pilot.name} is {'available' if is_available else 'NOT available'} for {start_date} to {end_date}. Current status: {pilot.status}"
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD."
    
    # ===== DRONE TOOLS =====
    def find_available_drones(self, location: Optional[str] = None, capability: Optional[str] = None) -> str:
        """Find available drones, optionally filtered by location and/or capability."""
        drones = self.db.get_available_drones(location=location, capability=capability)
        
        if not drones:
            return "No available drones found matching criteria."
        
        result = f"Available Drones ({len(drones)}):\n\n"
        for i, drone in enumerate(drones, 1):
            result += f"{i}. {drone.model} ({drone.drone_id})\n"
            result += f"   Capabilities: {', '.join(drone.capabilities)}\n"
            result += f"   Location: {drone.location}\n"
            result += f"   Status: {drone.status}\n\n"
        
        return result
    
    def get_drone_details(self, drone_id: str) -> str:
        """Get detailed information about a specific drone."""
        drone = self.db.get_drone_by_id(drone_id)
        if not drone:
            return f"Drone {drone_id} not found."
        
        result = f"Drone Details: {drone.model}\n\n"
        result += f"ID: {drone.drone_id}\n"
        result += f"Location: {drone.location}\n"
        result += f"Status: {drone.status}\n\n"
        result += f"Capabilities: {', '.join(drone.capabilities)}\n\n"
        result += f"Current Assignment: {drone.current_assignment or 'None'}\n"
        result += f"Maintenance Due: {drone.maintenance_due or 'Not scheduled'}\n"
        return result
    
    # ===== MISSION TOOLS =====
    def get_mission_details(self, mission_id: str) -> str:
        """Get details about a mission/project."""
        mission = self.db.get_mission_by_id(mission_id)
        if not mission:
            return f"Mission {mission_id} not found."
        
        result = f"Mission Details: {mission.project_id}\n\n"
        result += f"Client: {mission.client}\n"
        result += f"Location: {mission.location}\n"
        result += f"Priority: {mission.priority}\n\n"
        result += f"Schedule:\n"
        result += f"  Start: {mission.start_date.isoformat()}\n"
        result += f"  End: {mission.end_date.isoformat()}\n\n"
        result += f"Requirements:\n"
        result += f"  Skills: {', '.join(mission.required_skills)}\n"
        result += f"  Certifications: {', '.join(mission.required_certs)}\n\n"
        result += f"Assignments:\n"
        result += f"  Pilot: {mission.assigned_pilot or 'Not assigned'}\n"
        result += f"  Drone: {mission.assigned_drone or 'Not assigned'}\n"
        return result
    
    def list_all_missions(self) -> str:
        """List all missions."""
        if not self.db.missions:
            return "No missions found."
        
        result = f"All Missions ({len(self.db.missions)}):\n\n"
        for i, (mission_id, mission) in enumerate(self.db.missions.items(), 1):
            status = "Assigned" if mission.assigned_pilot else "Unassigned"
            result += f"{i}. {mission.project_id}\n"
            result += f"   Client: {mission.client}\n"
            result += f"   Location: {mission.location}\n"
            result += f"   Priority: {mission.priority}\n"
            result += f"   Status: {status}\n\n"
        
        return result
    
    # ===== ASSIGNMENT TOOLS =====
    def find_best_pilot_for_mission(self, mission_id: str) -> str:
        """Find the best available pilot for a mission."""
        mission = self.db.get_mission_by_id(mission_id)
        if not mission:
            return f"Mission {mission_id} not found."
        
        candidates = []
        for pilot in self.db.pilots.values():
            if pilot.status != "Available":
                continue
            if not pilot.has_skills(mission.required_skills):
                continue
            if not pilot.has_certifications(mission.required_certs):
                continue
            if pilot.location != mission.location:
                continue
            
            candidates.append(pilot)
        
        if not candidates:
            return f"No suitable pilots available for mission {mission_id}."
        
        # Return the first available (could add scoring logic here)
        best_pilot = candidates[0]
        result = f"Recommended Pilot for {mission_id}:\n\n"
        result += f"Name: {best_pilot.name} ({best_pilot.pilot_id})\n"
        result += f"Location: {best_pilot.location}\n"
        result += f"Skills: {', '.join(best_pilot.skills)}\n"
        result += f"Certifications: {', '.join(best_pilot.certifications)}\n"
        result += f"Status: {best_pilot.status}\n\n"
        result += "Reason: Has all required skills and certifications."
        return result
    
    def find_best_drone_for_mission(self, mission_id: str) -> str:
        """Find the best available drone for a mission."""
        mission = self.db.get_mission_by_id(mission_id)
        if not mission:
            return f"Mission {mission_id} not found."
        
        candidates = []
        for drone in self.db.drones.values():
            if not drone.is_available():
                continue
            if not drone.has_capabilities(mission.required_skills):  # Assuming capabilities match skills needed
                continue
            if drone.location != mission.location:
                continue
            
            candidates.append(drone)
        
        if not candidates:
            return f"No suitable drones available for mission {mission_id}."
        
        best_drone = candidates[0]
        result = f"Recommended Drone for {mission_id}:\n\n"
        result += f"Model: {best_drone.model} ({best_drone.drone_id})\n"
        result += f"Location: {best_drone.location}\n"
        result += f"Capabilities: {', '.join(best_drone.capabilities)}\n"
        result += f"Status: {best_drone.status}\n\n"
        result += "Reason: Has all required capabilities."
        return result
    
    def assign_pilot_to_mission(self, pilot_id: str, mission_id: str) -> str:
        """Assign a pilot to a mission."""
        pilot = self.db.get_pilot_by_id(pilot_id)
        mission = self.db.get_mission_by_id(mission_id)
        
        if not pilot:
            return f"Pilot {pilot_id} not found."
        if not mission:
            return f"Mission {mission_id} not found."
        
        # Check basic availability
        if pilot.status != "Available":
            return f"Pilot {pilot.name} is not available (status: {pilot.status})."
        
        if not pilot.has_skills(mission.required_skills):
            missing = [s for s in mission.required_skills if s not in pilot.skills]
            return f"Pilot {pilot.name} lacks required skills: {', '.join(missing)}"
        
        if not pilot.has_certifications(mission.required_certs):
            missing = [c for c in mission.required_certs if c not in pilot.certifications]
            return f"Pilot {pilot.name} lacks required certifications: {', '.join(missing)}"
        
        # Perform assignment
        self.db.update_pilot_status(pilot_id, "Assigned", mission_id)
        self.db.update_mission_assignment(mission_id, pilot_id, mission.assigned_drone)
        
        result = f"Assignment Successful\n\n"
        result += f"Pilot: {pilot.name} ({pilot_id})\n"
        result += f"Mission: {mission_id}\n\n"
        result += f"Assignment Details:\n"
        result += f"  Status: Assigned\n"
        result += f"  Start: {mission.start_date.isoformat()}\n"
        result += f"  End: {mission.end_date.isoformat()}\n"
        return result
    
    def assign_drone_to_mission(self, drone_id: str, mission_id: str) -> str:
        """Assign a drone to a mission."""
        drone = self.db.get_drone_by_id(drone_id)
        mission = self.db.get_mission_by_id(mission_id)
        
        if not drone:
            return f"Drone {drone_id} not found."
        if not mission:
            return f"Mission {mission_id} not found."
        
        if not drone.is_available():
            return f"Drone {drone.model} is not available (status: {drone.status})."
        
        self.db.update_drone_status(drone_id, "Deployed", mission_id)
        self.db.update_mission_assignment(mission_id, mission.assigned_pilot, drone_id)
        
        result = f"Assignment Successful\n\n"
        result += f"Drone: {drone.model} ({drone_id})\n"
        result += f"Mission: {mission_id}\n\n"
        result += f"Assignment Details:\n"
        result += f"  Status: Deployed\n"
        result += f"  Start: {mission.start_date.isoformat()}\n"
        result += f"  End: {mission.end_date.isoformat()}\n"
        return result
    
    # ===== CONFLICT DETECTION TOOLS =====
    def detect_conflicts(self) -> str:
        """Detect and report all conflicts."""
        conflicts = self.conflict_detector.detect_all_conflicts()
        
        if not conflicts:
            return "No conflicts detected. All assignments are valid!"
        
        result = f"Conflicts Detected ({len(conflicts)} total):\n\n"
        
        # Group by severity
        critical = [c for c in conflicts if c.severity == "critical"]
        major = [c for c in conflicts if c.severity == "major"]
        minor = [c for c in conflicts if c.severity == "minor"]
        
        if critical:
            result += "CRITICAL ISSUES:  \n"
            for i, c in enumerate(critical, 1):
                result += f"  {i}. {c.description}\n"
            result += "\n"
        
        if major:
            result += "MAJOR ISSUES:\n"
            for i, c in enumerate(major, 1):
                result += f"  {i}. {c.description}\n"
            result += "\n"
        
        if minor:
            result += "MINOR ISSUES:\n"
            for i, c in enumerate(minor, 1):
                result += f"  {i}. {c.description}\n"
        
        return result
    
    def check_mission_conflicts(self, mission_id: str) -> str:
        """Check for conflicts specific to a mission."""
        mission = self.db.get_mission_by_id(mission_id)
        if not mission:
            return f"Mission {mission_id} not found."
        
        conflicts = self.conflict_detector.detect_all_conflicts()
        mission_conflicts = [c for c in conflicts if c.affected_mission == mission_id]
        
        if not mission_conflicts:
            return f"No conflicts for mission {mission_id}."
        
        result = f"Conflicts for {mission_id}:\n\n"
        for i, c in enumerate(mission_conflicts, 1):
            severity_label = c.severity.upper()
            result += f"{i}. [{severity_label}] {c.description}\n"
        
        return result
    
    # ===== REASSIGNMENT TOOLS =====
    def find_alternative_pilot(self, current_pilot_id: str, mission_id: str) -> str:
        """Find an alternative pilot for a mission (for urgent reassignments)."""
        mission = self.db.get_mission_by_id(mission_id)
        if not mission:
            return f"Mission {mission_id} not found."
        
        alternatives = []
        for pilot in self.db.pilots.values():
            if pilot.pilot_id == current_pilot_id:
                continue
            if pilot.status != "Available":
                continue
            if not pilot.has_skills(mission.required_skills):
                continue
            if not pilot.has_certifications(mission.required_certs):
                continue
            # Location flexibility for urgent reassignments
            alternatives.append(pilot)
        
        if not alternatives:
            return f"No alternative pilots available for mission {mission_id}."
        
        result = f"Alternative Pilots for {mission_id}:\n\n"
        for i, pilot in enumerate(alternatives, 1):
            location_note = "(Same location)" if pilot.location == mission.location else "(Different location)"
            result += f"{i}. {pilot.name} ({pilot.pilot_id})\n"
            result += f"   Location: {pilot.location} {location_note}\n"
            result += f"   Status: {pilot.status}\n\n"
        
        return result
