#!/usr/bin/env python
"""Test script for system status feature."""
import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agent import DroneOperationsAgent

# Initialize agent
print("Initializing agent...")
agent = DroneOperationsAgent(csv_path="./sample-data")

# Test system status query
print("\nTesting 'Show system status' query:")
response = agent.process_query("Show system status")
print(response)
