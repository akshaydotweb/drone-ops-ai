"""Data loading and management for Drone Operations."""
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional
from models import Pilot, Drone, Mission

class DroneDatabase:
    """In-memory database for drone operations."""
    
    def __init__(self):
        self.pilots: Dict[str, Pilot] = {}
        self.drones: Dict[str, Drone] = {}
        self.missions: Dict[str, Mission] = {}
        self.use_google_sheets = False
        self.sheets_client = None
        self.spreadsheet_ids = {
            'pilots': None,
            'drones': None,
            'missions': None
        }
    
    def load_from_csv(self, pilot_csv: str, drone_csv: str, mission_csv: str):
        """Load data from CSV files."""
        self._load_pilots(pilot_csv)
        self._load_drones(drone_csv)
        self._load_missions(mission_csv)
    
    def load_from_separate_google_sheets(self, pilot_sheet_id: str, drone_sheet_id: str, mission_sheet_id: str):
        """Load data from 3 separate Google Sheets.
        
        Args:
            pilot_sheet_id: Google Sheets ID for pilot roster
            drone_sheet_id: Google Sheets ID for drone fleet
            mission_sheet_id: Google Sheets ID for missions
        """
        try:
            import gspread
            from google.oauth2 import service_account
            
            # Try to authenticate with service account
            scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            # Check for credentials file
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            if not os.path.exists(creds_file):
                print(f"WARNING: Google Sheets credentials not found at {creds_file}")
                print("  Falling back to CSV mode")
                return False
            
            creds = service_account.Credentials.from_service_account_file(
                creds_file, scopes=scope
            )
            self.sheets_client = gspread.authorize(creds)
            
            # Store IDs
            self.spreadsheet_ids = {
                'pilots': pilot_sheet_id,
                'drones': drone_sheet_id,
                'missions': mission_sheet_id
            }
            
            # Load data from each sheet
            self._load_pilots_from_separate_sheet(pilot_sheet_id)
            self._load_drones_from_separate_sheet(drone_sheet_id)
            self._load_missions_from_separate_sheet(mission_sheet_id)
            
            self.use_google_sheets = True
            print("OK: Connected to Google Sheets (separate sheets)")
            return True
            
        except ImportError:
            print("WARNING: Google Sheets libraries not installed")
            print("  Install: pip install gspread google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"WARNING: Could not load from Google Sheets: {e}")
            return False
    
    def load_from_separate_sheets(self, pilot_sheet_id: str, drone_sheet_id: str, mission_sheet_id: str):
        """Load data from 3 separate Google Sheets.
        
        Args:
            pilot_sheet_id: Google Sheets ID for pilot roster
            drone_sheet_id: Google Sheets ID for drone fleet
            mission_sheet_id: Google Sheets ID for missions
        """
        try:
            import gspread
            from google.oauth2 import service_account
            
            # Try to authenticate with service account
            scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            # Check for credentials file
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            if not os.path.exists(creds_file):
                print(f"WARNING: Google Sheets credentials not found at {creds_file}")
                print("  Falling back to CSV mode")
                return False
            
            creds = service_account.Credentials.from_service_account_file(
                creds_file, scopes=scope
            )
            self.sheets_client = gspread.authorize(creds)
            
            # Store IDs
            self.spreadsheet_ids = {
                'pilots': pilot_sheet_id,
                'drones': drone_sheet_id,
                'missions': mission_sheet_id
            }
            
            # Load data from each sheet
            self._load_pilots_from_separate_sheet(pilot_sheet_id)
            self._load_drones_from_separate_sheet(drone_sheet_id)
            self._load_missions_from_separate_sheet(mission_sheet_id)
            
            self.use_google_sheets = True
            print("OK: Connected to Google Sheets (separate sheets)")
            return True
            
        except ImportError:
            print("WARNING: Google Sheets libraries not installed")
            print("  Install: pip install gspread google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"WARNING: Could not load from Google Sheets: {e}")
            return False
    
    def _load_pilots_from_separate_sheet(self, sheet_id: str):
        """Load pilots from a separate Google Sheet."""
        try:
            sheet = self.sheets_client.open_by_key(sheet_id)
            ws = sheet.get_worksheet(0)  # First sheet
            records = ws.get_all_records()
            
            for row in records:
                if not row.get('pilot_id'):
                    continue
                
                pilot = Pilot(
                    pilot_id=row['pilot_id'].strip(),
                    name=row['name'].strip(),
                    skills=[s.strip() for s in row['skills'].split(',')],
                    certifications=[c.strip() for c in row['certifications'].split(',')],
                    location=row['location'].strip(),
                    status=row['status'].strip(),
                    current_assignment=row.get('current_assignment', '').strip() or None,
                    available_from=datetime.fromisoformat(row['available_from'].strip()) if row.get('available_from', '').strip() else None
                )
                self.pilots[pilot.pilot_id] = pilot
            
            print(f"  Loaded {len(self.pilots)} pilots from Google Sheets")
        except Exception as e:
            print(f"ERROR loading pilots from Google Sheets: {e}")
    
    def _load_drones_from_separate_sheet(self, sheet_id: str):
        """Load drones from a separate Google Sheet."""
        try:
            sheet = self.sheets_client.open_by_key(sheet_id)
            ws = sheet.get_worksheet(0)  # First sheet
            records = ws.get_all_records()
            
            for row in records:
                if not row.get('drone_id'):
                    continue
                
                drone = Drone(
                    drone_id=row['drone_id'].strip(),
                    model=row['model'].strip(),
                    capabilities=[c.strip() for c in row['capabilities'].split(',')],
                    status=row['status'].strip(),
                    location=row['location'].strip(),
                    current_assignment=row.get('current_assignment', '').strip() or None,
                    maintenance_due=datetime.fromisoformat(row['maintenance_due'].strip()) if row.get('maintenance_due', '').strip() else None
                )
                self.drones[drone.drone_id] = drone
            
            print(f"  Loaded {len(self.drones)} drones from Google Sheets")
        except Exception as e:
            print(f"ERROR loading drones from Google Sheets: {e}")
    
    def _load_missions_from_separate_sheet(self, sheet_id: str):
        """Load missions from a separate Google Sheet."""
        try:
            sheet = self.sheets_client.open_by_key(sheet_id)
            ws = sheet.get_worksheet(0)  # First sheet
            records = ws.get_all_records()
            
            for row in records:
                if not row.get('project_id'):
                    continue
                
                mission = Mission(
                    project_id=row['project_id'].strip(),
                    client=row['client'].strip(),
                    location=row['location'].strip(),
                    required_skills=[s.strip() for s in row['required_skills'].split(',')],
                    required_certs=[c.strip() for c in row['required_certs'].split(',')],
                    start_date=datetime.fromisoformat(row['start_date'].strip()),
                    end_date=datetime.fromisoformat(row['end_date'].strip()),
                    priority=row['priority'].strip(),
                    assigned_pilot=row.get('assigned_pilot', '').strip() or None,
                    assigned_drone=row.get('assigned_drone', '').strip() or None
                )
                self.missions[mission.project_id] = mission
            
            print(f"  Loaded {len(self.missions)} missions from Google Sheets")
        except Exception as e:
            print(f"ERROR loading missions from Google Sheets: {e}")
    
    def load_from_google_sheets(self, spreadsheet_id: str):
        """Load data from Google Sheets.
        
        Args:
            spreadsheet_id: The Google Sheets ID from URL
        """
        try:
            import gspread
            from google.oauth2 import service_account
            
            # Try to authenticate with service account
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Check for credentials file
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            if not os.path.exists(creds_file):
                print(f"WARNING: Google Sheets credentials not found at {creds_file}")
                print("  Falling back to CSV mode")
                return False
            
            creds = service_account.Credentials.from_service_account_file(
                creds_file, scopes=scope
            )
            self.sheets_client = gspread.authorize(creds)
            self.spreadsheet_ids['pilots'] = spreadsheet_id
            
            # Load data from each sheet
            sheet = self.sheets_client.open_by_key(spreadsheet_id)
            
            self._load_pilots_from_sheets(sheet)
            self._load_drones_from_sheets(sheet)
            self._load_missions_from_sheets(sheet)
            
            self.use_google_sheets = True
            print("OK: Connected to Google Sheets")
            return True
            
        except ImportError:
            print("WARNING: Google Sheets libraries not installed")
            print("  Install: pip install gspread google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"WARNING: Could not load from Google Sheets: {e}")
            print("  Falling back to CSV mode")
            return False
    
    def load_from_separate_google_sheets(self, pilot_sheet_id: str, drone_sheet_id: str, mission_sheet_id: str):
        """Load data from 3 separate Google Sheets.
        
        Args:
            pilot_sheet_id: Spreadsheet ID for pilots
            drone_sheet_id: Spreadsheet ID for drones
            mission_sheet_id: Spreadsheet ID for missions
        """
        try:
            import gspread
            from google.oauth2 import service_account
            
            scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            
            creds_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
            if not os.path.exists(creds_file):
                print(f"WARNING: Google Sheets credentials not found at {creds_file}")
                print("  Falling back to CSV mode")
                return False
            
            creds = service_account.Credentials.from_service_account_file(
                creds_file, scopes=scope
            )
            self.sheets_client = gspread.authorize(creds)
            self.pilot_sheet_id = pilot_sheet_id
            self.drone_sheet_id = drone_sheet_id
            self.mission_sheet_id = mission_sheet_id
            
            # Load pilots
            pilot_sheet = self.sheets_client.open_by_key(pilot_sheet_id)
            self._load_pilots_from_separate_sheet(pilot_sheet)
            
            # Load drones
            drone_sheet = self.sheets_client.open_by_key(drone_sheet_id)
            self._load_drones_from_separate_sheet(drone_sheet)
            
            # Load missions
            mission_sheet = self.sheets_client.open_by_key(mission_sheet_id)
            self._load_missions_from_separate_sheet(mission_sheet)
            
            self.use_google_sheets = True
            print("OK: Connected to separate Google Sheets")
            print(f"  Pilots: {pilot_sheet_id[:20]}...")
            print(f"  Drones: {drone_sheet_id[:20]}...")
            print(f"  Missions: {mission_sheet_id[:20]}...")
            return True
            
        except ImportError:
            print("WARNING: Google Sheets libraries not installed")
            print("  Install: pip install gspread google-auth-oauthlib")
            return False
        except Exception as e:
            print(f"WARNING: Could not load from Google Sheets: {e}")
            print("  Falling back to CSV mode")
            return False
    
    def _load_pilots_from_separate_sheet(self, sheet):
        """Load pilots from a separate Google Sheet."""
        try:
            # Try 'Pilots' tab first, then 'Sheet1' or first available
            try:
                ws = sheet.worksheet('Pilots')
            except:
                ws = sheet.sheet1
            
            records = ws.get_all_records()
            for row in records:
                if not row.get('pilot_id'):
                    continue
                pilot = Pilot(
                    pilot_id=row['pilot_id'],
                    name=row['name'],
                    skills=[s.strip() for s in row['skills'].split(',')],
                    certifications=[c.strip() for c in row['certifications'].split(',')],
                    location=row['location'],
                    status=row['status'],
                    current_assignment=row.get('current_assignment') or None,
                    available_from=datetime.fromisoformat(row['available_from']) if row.get('available_from') else None
                )
                self.pilots[pilot.pilot_id] = pilot
            print(f"  Loaded {len(self.pilots)} pilots")
        except Exception as e:
            print(f"ERROR loading pilots: {e}")
    
    def _load_drones_from_separate_sheet(self, sheet):
        """Load drones from a separate Google Sheet."""
        try:
            try:
                ws = sheet.worksheet('Drones')
            except:
                ws = sheet.sheet1
            
            records = ws.get_all_records()
            for row in records:
                if not row.get('drone_id'):
                    continue
                drone = Drone(
                    drone_id=row['drone_id'],
                    model=row['model'],
                    capabilities=[c.strip() for c in row['capabilities'].split(',')],
                    status=row['status'],
                    location=row['location'],
                    current_assignment=row.get('current_assignment') or None,
                    maintenance_due=datetime.fromisoformat(row['maintenance_due']) if row.get('maintenance_due') else None
                )
                self.drones[drone.drone_id] = drone
            print(f"  Loaded {len(self.drones)} drones")
        except Exception as e:
            print(f"ERROR loading drones: {e}")
    
    def _load_missions_from_separate_sheet(self, sheet):
        """Load missions from a separate Google Sheet."""
        try:
            try:
                ws = sheet.worksheet('Missions')
            except:
                ws = sheet.sheet1
            
            records = ws.get_all_records()
            for row in records:
                if not row.get('project_id'):
                    continue
                mission = Mission(
                    project_id=row['project_id'],
                    client=row['client'],
                    location=row['location'],
                    required_skills=[s.strip() for s in row['required_skills'].split(',')],
                    required_certs=[c.strip() for c in row['required_certs'].split(',')],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    priority=row['priority'],
                    assigned_pilot=row.get('assigned_pilot') or None,
                    assigned_drone=row.get('assigned_drone') or None
                )
                self.missions[mission.project_id] = mission
            print(f"  Loaded {len(self.missions)} missions")
        except Exception as e:
            print(f"ERROR loading missions: {e}")
    
    def _load_pilots_from_sheets(self, sheet):
        """Load pilots from Google Sheets."""
        try:
            ws = sheet.worksheet('Pilots')
            records = ws.get_all_records()
            for row in records:
                if not row.get('pilot_id'):
                    continue
                pilot = Pilot(
                    pilot_id=row['pilot_id'],
                    name=row['name'],
                    skills=[s.strip() for s in row['skills'].split(',')],
                    certifications=[c.strip() for c in row['certifications'].split(',')],
                    location=row['location'],
                    status=row['status'],
                    current_assignment=row.get('current_assignment') or None,
                    available_from=datetime.fromisoformat(row['available_from']) if row.get('available_from') else None
                )
                self.pilots[pilot.pilot_id] = pilot
        except Exception as e:
            print(f"ERROR loading pilots from Google Sheets: {e}")
    
    def _load_drones_from_sheets(self, sheet):
        """Load drones from Google Sheets."""
        try:
            ws = sheet.worksheet('Drones')
            records = ws.get_all_records()
            for row in records:
                if not row.get('drone_id'):
                    continue
                drone = Drone(
                    drone_id=row['drone_id'],
                    model=row['model'],
                    capabilities=[c.strip() for c in row['capabilities'].split(',')],
                    status=row['status'],
                    location=row['location'],
                    current_assignment=row.get('current_assignment') or None,
                    maintenance_due=datetime.fromisoformat(row['maintenance_due']) if row.get('maintenance_due') else None
                )
                self.drones[drone.drone_id] = drone
        except Exception as e:
            print(f"ERROR loading drones from Google Sheets: {e}")
    
    def _load_missions_from_sheets(self, sheet):
        """Load missions from Google Sheets."""
        try:
            ws = sheet.worksheet('Missions')
            records = ws.get_all_records()
            for row in records:
                if not row.get('project_id'):
                    continue
                mission = Mission(
                    project_id=row['project_id'],
                    client=row['client'],
                    location=row['location'],
                    required_skills=[s.strip() for s in row['required_skills'].split(',')],
                    required_certs=[c.strip() for c in row['required_certs'].split(',')],
                    start_date=datetime.fromisoformat(row['start_date']),
                    end_date=datetime.fromisoformat(row['end_date']),
                    priority=row['priority'],
                    assigned_pilot=row.get('assigned_pilot') or None,
                    assigned_drone=row.get('assigned_drone') or None
                )
                self.missions[mission.project_id] = mission
        except Exception as e:
            print(f"ERROR loading missions from Google Sheets: {e}")
    
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
            
            # Sync to Google Sheets if enabled
            if self.use_google_sheets:
                self._sync_mission_to_sheets(mission_id)
    
    def sync_to_google_sheets(self):
        """Sync all current data to Google Sheets."""
        if not self.use_google_sheets or not self.sheets_client:
            return False
        
        try:
            sheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            self._sync_pilots_to_sheets(sheet)
            self._sync_drones_to_sheets(sheet)
            self._sync_missions_to_sheets(sheet)
            print("OK: Data synced to Google Sheets")
            return True
        except Exception as e:
            print(f"ERROR syncing to Google Sheets: {e}")
            return False
    
    def _sync_pilots_to_sheets(self, sheet):
        """Sync pilot data to Google Sheets."""
        try:
            ws = sheet.worksheet('Pilots')
            rows = []
            for pilot in self.pilots.values():
                rows.append([
                    pilot.pilot_id,
                    pilot.name,
                    ', '.join(pilot.skills),
                    ', '.join(pilot.certifications),
                    pilot.location,
                    pilot.status,
                    pilot.current_assignment or '',
                    pilot.available_from.isoformat() if pilot.available_from else ''
                ])
            
            # Clear and update
            ws.clear()
            ws.append_row(['pilot_id', 'name', 'skills', 'certifications', 'location', 'status', 'current_assignment', 'available_from'])
            ws.append_rows(rows)
            print("  Pilots synced")
        except Exception as e:
            print(f"  ERROR syncing pilots: {e}")
    
    def _sync_drones_to_sheets(self, sheet):
        """Sync drone data to Google Sheets."""
        try:
            ws = sheet.worksheet('Drones')
            rows = []
            for drone in self.drones.values():
                rows.append([
                    drone.drone_id,
                    drone.model,
                    ', '.join(drone.capabilities),
                    drone.status,
                    drone.location,
                    drone.current_assignment or '',
                    drone.maintenance_due.isoformat() if drone.maintenance_due else ''
                ])
            
            # Clear and update
            ws.clear()
            ws.append_row(['drone_id', 'model', 'capabilities', 'status', 'location', 'current_assignment', 'maintenance_due'])
            ws.append_rows(rows)
            print("  Drones synced")
        except Exception as e:
            print(f"  ERROR syncing drones: {e}")
    
    def _sync_missions_to_sheets(self, sheet):
        """Sync mission data to Google Sheets."""
        try:
            ws = sheet.worksheet('Missions')
            rows = []
            for mission in self.missions.values():
                rows.append([
                    mission.project_id,
                    mission.client,
                    mission.location,
                    ', '.join(mission.required_skills),
                    ', '.join(mission.required_certs),
                    mission.start_date.isoformat(),
                    mission.end_date.isoformat(),
                    mission.priority,
                    mission.assigned_pilot or '',
                    mission.assigned_drone or ''
                ])
            
            # Clear and update
            ws.clear()
            ws.append_row(['project_id', 'client', 'location', 'required_skills', 'required_certs', 'start_date', 'end_date', 'priority', 'assigned_pilot', 'assigned_drone'])
            ws.append_rows(rows)
            print("  Missions synced")
        except Exception as e:
            print(f"  ERROR syncing missions: {e}")
    
    def _sync_mission_to_sheets(self, mission_id: str):
        """Sync single mission update to Google Sheets."""
        try:
            if not self.sheets_client:
                return
            
            sheet = self.sheets_client.open_by_key(self.spreadsheet_id)
            ws = sheet.worksheet('Missions')
            mission = self.missions.get(mission_id)
            
            if not mission:
                return
            
            # Find and update the row
            records = ws.get_all_records()
            for i, record in enumerate(records, start=2):
                if record.get('project_id') == mission_id:
                    ws.update_cell(i, 9, mission.assigned_pilot or '')  # Column I
                    ws.update_cell(i, 10, mission.assigned_drone or '')  # Column J
                    print(f"  Updated mission {mission_id} in Sheets")
                    break
        except Exception as e:
            print(f"  WARNING: Could not sync mission {mission_id}: {e}")
