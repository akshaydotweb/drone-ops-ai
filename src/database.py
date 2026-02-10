"""Data loading and management for Drone Operations."""
import csv
from datetime import datetime
from typing import List, Dict, Optional
from models import Pilot, Drone, Mission

class DroneDatabase:
    """In-memory database for drone operations."""
    
    def __init__(self):
        self.pilots: Dict[str, Pilot] = {}
        self.drones: Dict[str, Drone] = {}
        self.missions: Dict[str, Mission] = {}
    
    def load_from_csv(self, pilot_csv: str, drone_csv: str, mission_csv: str):
        """Load data from CSV files."""
        self._load_pilots(pilot_csv)
        self._load_drones(drone_csv)
        self._load_missions(mission_csv)
    
    def _load_pilots(self, filename: str):
        """Load pilots from CSV."""
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                pilot = Pilot(
                    pilot_id=row['pilot_id'],
                    name=row['name'],
                    skills=[s.strip() for s in row['skills'].split(',')],
                    certifications=[c.strip() for c in row['certifications'].split(',')],
                    location=row['location'],
                    status=row['status'],
                    current_assignment=row.get('current_assignment', None) or None,
                    available_from=datetime.fromisoformat(row['available_from']) if row.get('available_from') else None
                )
                self.pilots[pilot.pilot_id] = pilot
    
    def _load_drones(self, filename: str):
        """Load drones from CSV."""
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                drone = Drone(
                    drone_id=row['drone_id'],
                    model=row['model'],
                    capabilities=[c.strip() for c in row['capabilities'].split(',')],
                    status=row['status'],
                    location=row['location'],
                    current_assignment=row.get('current_assignment', None) or None,
                    maintenance_due=datetime.fromisoformat(row['maintenance_due']) if row.get('maintenance_due') else None
                )
                self.drones[drone.drone_id] = drone
    
    def _load_missions(self, filename: str):
        """Load missions from CSV."""
        with open(filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                mission = Mission(
                    project_id=row['project_id'],
                    client=row['client'],
                    location=row['location'],
                    required_skills=[s.strip() for s in row['required_skills'].split(',')],
                    required_certs=[c.strip() for c in row['required_certs'].split(',')],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    priority=row['priority']
                )
                self.missions[mission.project_id] = mission
    
    # Query methods
    def get_available_pilots(self, location: Optional[str] = None, skill: Optional[str] = None) -> List[Pilot]:
        """Get all available pilots, optionally filtered."""
        pilots = [p for p in self.pilots.values() if p.status == "Available"]
        if location:
            pilots = [p for p in pilots if p.location == location]
        if skill:
            pilots = [p for p in pilots if skill in p.skills]
        return pilots
    
    def get_available_drones(self, location: Optional[str] = None, capability: Optional[str] = None) -> List[Drone]:
        """Get all available drones, optionally filtered."""
        drones = [d for d in self.drones.values() if d.is_available()]
        if location:
            drones = [d for d in drones if d.location == location]
        if capability:
            drones = [d for d in drones if capability in d.capabilities]
        return drones
    
    def get_pilot_by_id(self, pilot_id: str) -> Optional[Pilot]:
        """Get pilot by ID."""
        return self.pilots.get(pilot_id)
    
    def get_drone_by_id(self, drone_id: str) -> Optional[Drone]:
        """Get drone by ID."""
        return self.drones.get(drone_id)
    
    def get_mission_by_id(self, mission_id: str) -> Optional[Mission]:
        """Get mission by ID."""
        return self.missions.get(mission_id)
    
    def update_pilot_status(self, pilot_id: str, status: str, assignment: Optional[str] = None):
        """Update pilot status and assignment."""
        if pilot_id in self.pilots:
            self.pilots[pilot_id].status = status
            self.pilots[pilot_id].current_assignment = assignment
    
    def update_drone_status(self, drone_id: str, status: str, assignment: Optional[str] = None):
        """Update drone status and assignment."""
        if drone_id in self.drones:
            self.drones[drone_id].status = status
            self.drones[drone_id].current_assignment = assignment
    
    def update_mission_assignment(self, mission_id: str, pilot_id: Optional[str], drone_id: Optional[str]):
        """Update mission assignment."""
        if mission_id in self.missions:
            self.missions[mission_id].assigned_pilot = pilot_id
            self.missions[mission_id].assigned_drone = drone_id
