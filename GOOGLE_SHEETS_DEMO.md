Google Sheets Demo Setup (Quick)

For demonstration purposes, you can upload your CSV data to Google Sheets without setting up authentication.

Step 1: Create Free Google Account
Go to https://accounts.google.com
Create new account (skip if you already have one)

Step 2: Create New Google Sheet
1. Visit https://sheets.google.com
2. Click "New" (+ button)
3. Click "Spreadsheet"
4. Name it: "Drone Operations Data Demo"

Step 3: Prepare Pilot Data
1. Open file: sample-data/pilot_roster.csv
2. Copy all content (Ctrl+A, Ctrl+C)
3. In Google Sheets, click Sheet tab at bottom
4. Rename to "Pilots"
5. Click cell A1, paste data (Ctrl+V)
6. Format as needed (auto-fit columns)

Step 4: Add Drones Sheet
1. Click "+" at bottom to add new sheet
2. Name it "Drones"
3. Open: sample-data/drone_fleet.csv
4. Copy and paste all content to this sheet

Step 5: Add Missions Sheet
1. Click "+" at bottom to add new sheet
2. Name it "Missions"
3. Open: sample-data/missions.csv
4. Copy and paste all content to this sheet

Step 6: Share Your Sheet
1. Click "Share" button (top right)
2. Choose who can access (e.g., "Anyone with link")
3. Copy the sharing URL
4. Share with reviewers: "Here's the data: [URL]"

Step 7: Get Spreadsheet ID (Optional)
From URL: https://docs.google.com/spreadsheets/d/{ID}/edit

Example:
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j1k/edit

The ID is: 1a2b3c4d5e6f7g8h9i0j1k

Result

You now have:
- Live Google Sheet with all drone operations data
- Shareable link for reviewers
- Demo of data structure
- Can edit missions/pilots directly in Sheets

CSV Data Structure

Pilots:
- pilot_id: P001, P002, etc.
- name: Arjun, Priya, etc.
- skills: Mapping, Survey, etc.
- certifications: DGCA, Night Ops, etc.
- location: Bangalore, Mumbai, etc.
- status: Available, On Leave, etc.

Drones:
- drone_id: D001, D002, etc.
- model: DJI Phantom 4, etc.
- capabilities: Mapping, Video, etc.
- status: Available, Maintenance, etc.
- location: Bangalore, Mumbai, etc.

Missions:
- project_id: PRJ001, PRJ002, etc.
- client: TechCorp, CloudBuilders, etc.
- location: Bangalore, Mumbai, etc.
- required_skills: Mapping, Survey, etc.
- required_certs: DGCA, Night Ops, etc.
- start_date: 2026-02-12
- end_date: 2026-02-18
- priority: High, Standard, Urgent
- assigned_pilot: P001 (once assigned)
- assigned_drone: D001 (once assigned)

Tips

1. Use Format > Freeze to freeze headers
2. Use Data > Create a filter to filter by status
3. Share with Viewer access if you don't want edits
4. Download as CSV later if needed (File > Download)
5. Create charts from the data (Insert > Chart)

Demonstrating Sync

Once the app is running and Google Sheets is set up:
1. Make an assignment: "Assign P001 to PRJ001"
2. Check Google Sheet - assigned_pilot column updates
3. Shows 2-way sync working

For submission, you can:
- Share this Google Sheet link with reviewers
- Show it alongside your app
- Explain: "Demo data is here, app reads/writes to Google Sheets"
