"""Main Drone Operations Coordinator Agent."""
import os
from dotenv import load_dotenv
from typing import Dict, Any
import json
from database import DroneDatabase
from tools import DroneOperationsTools
from datetime import datetime

load_dotenv()

class DroneOperationsAgent:
    """Main AI Agent for drone operations coordination."""
    
    def __init__(self, csv_path: str = "../sample-data"):
        """Initialize the agent with data from CSV files."""
        self.db = DroneDatabase()
        
        # Load data
        self.db.load_from_csv(
            pilot_csv=f"{csv_path}/pilot_roster.csv",
            drone_csv=f"{csv_path}/drone_fleet.csv",
            mission_csv=f"{csv_path}/missions.csv"
        )
        
        self.tools = DroneOperationsTools(self.db)
        self.conversation_history = []
        
        # Try to initialize LLM
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM (ChatGPT or Claude)."""
        try:
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI-API")
            if not api_key:
                print("WARNING: OPENAI_API_KEY not found in .env")
                return None
            
            llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key, temperature=0.7)
            print("OK: Connected to OpenAI ChatGPT")
            return llm
        except Exception as e:
            print(f"WARNING: Could not initialize ChatOpenAI: {e}")
            print("   Using fallback rule-based mode...")
            return None
    
    def process_query(self, user_query: str) -> str:
        """Process a user query and return a response."""
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # If we have LLM, use it; otherwise use rule-based mode
        if self.llm:
            try:
                response = self._process_with_llm(user_query)
            except Exception as e:
                print(f"LLM error: {e}")
                response = self._process_rule_based(user_query)
        else:
            response = self._process_rule_based(user_query)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _process_with_llm(self, user_query: str) -> str:
        """Process query using the LLM with tools."""
        try:
            from langchain.tools import Tool
            from langchain.agents import tool
            
            # Create tool descriptions for the LLM
            tools_list = [
                Tool(
                    name="Find Available Pilots",
                    func=lambda location=None: self.tools.find_available_pilots(location),
                    description="Find available pilots. Optional: filter by location."
                ),
                Tool(
                    name="Find Available Drones",
                    func=lambda location=None: self.tools.find_available_drones(location),
                    description="Find available drones. Optional: filter by location."
                ),
                Tool(
                    name="Get Mission Details",
                    func=self.tools.get_mission_details,
                    description="Get detailed information about a specific mission. Pass mission_id."
                ),
                Tool(
                    name="Find Best Pilot for Mission",
                    func=self.tools.find_best_pilot_for_mission,
                    description="Find the best pilot for a mission. Pass mission_id."
                ),
                Tool(
                    name="Find Best Drone for Mission",
                    func=self.tools.find_best_drone_for_mission,
                    description="Find the best drone for a mission. Pass mission_id."
                ),
                Tool(
                    name="Assign Pilot to Mission",
                    func=lambda pilot_id, mission_id: self.tools.assign_pilot_to_mission(pilot_id, mission_id),
                    description="Assign a pilot to a mission. Pass pilot_id and mission_id."
                ),
                Tool(
                    name="Detect Conflicts",
                    func=lambda: self.tools.detect_conflicts(),
                    description="Detect and report all conflicts in current assignments."
                ),
                Tool(
                    name="List All Missions",
                    func=lambda: self.tools.list_all_missions(),
                    description="List all available missions."
                )
            ]
            
            # Call LLM with tools
            messages = [{
                "role": "user",
                "content": f"""You are a Drone Operations Coordinator AI Agent. Your role is to help with:
1. Pilot roster management
2. Drone inventory tracking
3. Mission assignment coordination
4. Conflict detection and resolution

User Query: {user_query}

Use the available tools to answer the user's question. Be conversational and helpful."""
            }]
            
            response = self.llm.invoke(messages)
            
            # Extract text from response
            if hasattr(response, 'content'):
                return response.content
            else:
                return str(response)
        
        except Exception as e:
            return f"Error processing with LLM: {str(e)}. Falling back to rule-based response..."
    
    def _process_rule_based(self, user_query: str) -> str:
        """Process query using rule-based logic (fallback mode)."""
        import re
        
        # Handle empty queries
        if not user_query or not user_query.strip():
            return "Please enter a query. Type 'help' to see available commands."
        
        query_lower = user_query.lower()
        
        # Pattern matching for common queries
        if ("available" in query_lower or "all" in query_lower) and "pilot" in query_lower:
            location = self._extract_location(user_query)
            result = self.tools.find_available_pilots(location=location)
            if "No available pilots" in result and location:
                return f"ERROR: No available pilots found in {location}. Try another location or check 'List all missions' for options."
            return result
        
        elif ("available" in query_lower or "all" in query_lower) and "drone" in query_lower:
            location = self._extract_location(user_query)
            result = self.tools.find_available_drones(location=location)
            if "No available drones" in result and location:
                return f"ERROR: No available drones found in {location}. Check maintenance status or location."
            return result
        
        elif "best pilot" in query_lower and "for" in query_lower:
            mission_id = self._extract_mission_id(user_query)
            if mission_id:
                result = self.tools.find_best_pilot_for_mission(mission_id)
                if "No suitable pilots" in result:
                    return f"ERROR: No suitable pilots available for {mission_id}.\n\nTry:\n- 'Reassign pilot for {mission_id}' for alternatives\n- 'Show available pilots' to see all pilots"
                return result
            return "ERROR: Mission ID not found. Specify mission ID (e.g., PRJ001).\n\nUsage: 'Best pilot for PRJ001'"
        
        elif "best drone" in query_lower and "for" in query_lower:
            mission_id = self._extract_mission_id(user_query)
            if mission_id:
                result = self.tools.find_best_drone_for_mission(mission_id)
                if "No suitable drones" in result:
                    return f"ERROR: No suitable drones available for {mission_id}.\n\nTry:\n- 'Show available drones' to check drone status\n- 'Detect conflicts' to identify issues"
                return result
            return "ERROR: Mission ID not found. Specify mission ID.\n\nUsage: 'Best drone for PRJ001'"
        
        elif "mission" in query_lower and ("details" in query_lower or "info" in query_lower):
            mission_id = self._extract_mission_id(user_query)
            if mission_id:
                return self.tools.get_mission_details(mission_id)
            else:
                return "NOTE: Mission ID not specified. List available missions first:\n'What missions are available?'\n\nThen use: 'Mission details PRJ001'"
        
        elif "mission" in query_lower and ("available" in query_lower or "list" in query_lower or "what" in query_lower or "all" in query_lower or "show" in query_lower):
            return self.tools.list_all_missions()
        
        elif "assign" in query_lower and ("pilot" in query_lower or re.search(r'\bp\d+', user_query, re.IGNORECASE)):
            pilot_id = self._extract_pilot_id(user_query)
            mission_id = self._extract_mission_id(user_query)
            
            if not pilot_id and not mission_id:
                return "ERROR: Missing both pilot ID and mission ID.\n\nUsage: 'Assign P001 to PRJ001'\n\nOr get suggestions:\n'Best pilot for PRJ001'"
            elif not pilot_id:
                return f"ERROR: Pilot ID not found.\n\nUsage: 'Assign P001 to {mission_id if mission_id else 'PRJ001'}'\n\nFind pilots: 'Show available pilots'"
            elif not mission_id:
                return f"ERROR: Mission ID not found.\n\nUsage: 'Assign {pilot_id} to PRJ001'\n\nList missions: 'What missions are available?'"
            
            return self.tools.assign_pilot_to_mission(pilot_id, mission_id)
        
        elif "assign" in query_lower and ("drone" in query_lower or re.search(r'\bd\d+', user_query, re.IGNORECASE)):
            drone_id = self._extract_drone_id(user_query)
            mission_id = self._extract_mission_id(user_query)
            
            if not drone_id and not mission_id:
                return "ERROR: Missing both drone ID and mission ID.\n\nUsage: 'Assign D001 to PRJ001'\n\nOr get suggestions:\n'Best drone for PRJ001'"
            elif not drone_id:
                return f"ERROR: Drone ID not found.\n\nUsage: 'Assign D001 to {mission_id if mission_id else 'PRJ001'}'\n\nFind drones: 'Show available drones'"
            elif not mission_id:
                return f"ERROR: Mission ID not found.\n\nUsage: 'Assign {drone_id} to PRJ001'\n\nList missions: 'What missions are available?'"
            
            return self.tools.assign_drone_to_mission(drone_id, mission_id)
        
        elif "conflict" in query_lower or "detect" in query_lower and "conflict" in query_lower:
            return self.tools.detect_conflicts()
        
        elif "alternative" in query_lower or "reassign" in query_lower:
            mission_id = self._extract_mission_id(user_query)
            pilot_id = self._extract_pilot_id(user_query)
            
            if mission_id and pilot_id:
                return self.tools.find_alternative_pilot(pilot_id, mission_id)
            elif mission_id:
                result = self.tools.find_best_pilot_for_mission(mission_id)
                if "No suitable pilots" in result:
                    return f"ERROR: No suitable pilots for reassignment to {mission_id}.\n\nAction: Review mission requirements or check 'Show available pilots'"
                return result
            else:
                return "ERROR: Mission ID not specified for reassignment.\n\nUsage: 'Reassign pilot for PRJ001'\n\nList missions: 'What missions are available?'"
        
        elif "help" in query_lower or "?" in query_lower:
            return self._get_help_text()
        
        else:
            # Suggest closest match based on keywords
            suggestions = []
            if any(word in query_lower for word in ["pilot", "drone", "available"]):
                suggestions.append("  • 'Show available pilots' - List all available pilots")
                suggestions.append("  • 'Show available drones' - List all available drones")
            if any(word in query_lower for word in ["mission", "project", "assignment"]):
                suggestions.append("  • 'What missions are available?' - List all missions")
                suggestions.append("  • 'Mission details PRJ001' - Get mission details")
            if any(word in query_lower for word in ["assign", "add", "allocate"]):
                suggestions.append("  • 'Assign P001 to PRJ001' - Assign pilot to mission")
                suggestions.append("  • 'Assign D001 to PRJ001' - Assign drone to mission")
            if any(word in query_lower for word in ["conflict", "issue", "problem", "check"]):
                suggestions.append("  • 'Detect conflicts' - Check for scheduling/skill issues")
            
            if suggestions:
                return f"ERROR: Query not recognized. Did you mean?\n\n" + "\n".join(suggestions) + "\n\nType 'help' for all commands."
            else:
                return "ERROR: I didn't understand that query.\n\nTry:\n  • 'Show available pilots'\n  • 'What missions are available?'\n  • 'Assign P001 to PRJ001'\n  • 'Detect conflicts'\n\nType 'help' for complete list of commands."
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text."""
        locations = ["bangalore", "mumbai", "delhi", "pune"]
        text_lower = text.lower()
        for loc in locations:
            if loc in text_lower:
                return loc.capitalize()
        return None
    
    def _extract_mission_id(self, text: str) -> str:
        """Extract mission ID from text."""
        import re
        match = re.search(r'PRJ\d+', text, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return None
    
    def _extract_pilot_id(self, text: str) -> str:
        """Extract pilot ID from text."""
        import re
        match = re.search(r'P\d+', text, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return None
    
    def _extract_drone_id(self, text: str) -> str:
        """Extract drone ID from text."""
        import re
        match = re.search(r'D\d+', text, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return None
    
    def _get_help_text(self) -> str:
        """Return comprehensive help text."""
        return """Drone Operations Coordinator Agent v1.0
        
PILOT MANAGEMENT:
  • "Show available pilots" - List all available pilots with skills
  • "Show all pilots" or "All pilots" - Same as above
  • "Show available pilots in [location]" - Filter pilots by location
    Examples: Bangalore, Mumbai, Delhi, Pune
  • "Best pilot for [mission_id]" - Find best pilot for a mission
    Example: "Best pilot for PRJ001"

DRONE MANAGEMENT:
  • "Show available drones" - List all available drones
  • "Show all drones" or "All drones" - Same as above
  • "Show available drones in [location]" - Filter drones by location
  • "Best drone for [mission_id]" - Find best drone for a mission
    Example: "Best drone for PRJ001"

MISSION MANAGEMENT:
  • "What missions are available?" - List all missions
  • "Show all missions" or "List all missions" - Same as above
  • "All missions" - Same as above
  • "Mission details [mission_id]" - Get full mission details
    Example: "Mission details PRJ001"

ASSIGNMENTS:
  • "Assign [pilot_id] to [mission_id]" - Assign a pilot to mission
    Example: "Assign P001 to PRJ001"
  • "Assign [drone_id] to [mission_id]" - Assign a drone to mission
    Example: "Assign D001 to PRJ001"
  • "Reassign pilot for [mission_id]" - Find alternative pilots
    Example: "Reassign pilot for PRJ001"

CONFLICT MANAGEMENT:
  • "Detect conflicts" - Check for any scheduling or skill issues
  • "Find conflicts" - Same as above
  • "Check for conflicts" - Same as above

EXAMPLES:
  • "Show all pilots in Bangalore" - Pilots in Bangalore
  • "Best pilot for PRJ002" - Recommended pilot with reasoning
  • "Assign P003 to PRJ001" - Make assignment
  • "Detect conflicts" - Check all conflicts

REFERENCE:
  Pilot IDs: P001, P002, P003, P004
  Drone IDs: D001, D002, D003, D004
  Mission IDs: PRJ001, PRJ002, PRJ003
  Locations: Bangalore, Mumbai, Delhi, Pune

Type any of the above commands to get started!
"""
    
    def get_database_summary(self) -> str:
        """Get a summary of current database state."""
        summary = f"""
Current Drone Operations Summary:

Pilots: {len(self.db.pilots)} total
  - Available: {len([p for p in self.db.pilots.values() if p.status == 'Available'])}
  - Assigned: {len([p for p in self.db.pilots.values() if p.status == 'Assigned'])}
  - On Leave: {len([p for p in self.db.pilots.values() if p.status == 'On Leave'])}

Drones: {len(self.db.drones)} total
  - Available: {len([d for d in self.db.drones.values() if d.is_available()])}
  - In Maintenance: {len([d for d in self.db.drones.values() if d.is_in_maintenance()])}
  - Deployed: {len([d for d in self.db.drones.values() if d.status == 'Deployed'])}

Missions: {len(self.db.missions)} total
  - Unassigned: {len([m for m in self.db.missions.values() if not m.assigned_pilot])}
  - Assigned: {len([m for m in self.db.missions.values() if m.assigned_pilot])}
"""
        return summary
