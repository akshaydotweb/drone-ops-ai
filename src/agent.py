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
    
    