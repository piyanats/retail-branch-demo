#!/usr/bin/env python3
"""Create test user for development and testing"""

from google.cloud import bigquery
import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
DATASET_ID = os.getenv('DATASET_ID', 'retail_branches')

if not PROJECT_ID:
    print("❌ ERROR: PROJECT_ID not set in .env file")
    sys.exit(1)

print("=" * 60)
print("Create Test User for Retail Branch Management System")
print("=" * 60)

# Initialize BigQuery client
try:
    client = bigquery.Client(project=PROJECT_ID)
    print("✅ Connected to BigQuery")
except Exception as e:
    print(f"❌ Failed to connect to BigQuery: {e}")
    sys.exit(1)

# Get user email
print("\nEnter test user information:")
email = input("Email address (e.g., your-email@gmail.com): ").strip()

if not email or '@' not in email:
    print("❌ Invalid email address")
    sys.exit(1)

name = input("Full name (e.g., Test User): ").strip() or "Test User"

print("\nSelect user level:")
print("1. admin    - Full access to everything")
print("2. manager  - Manage teams")
print("3. editor   - Edit data")
print("4. viewer   - Read-only access")

level_choice = input("Choose (1-4) [default: 1]: ").strip() or "1"
user_levels = {"1": "admin", "2": "manager", "3": "editor", "4": "viewer"}
user_level = user_levels.get(level_choice, "admin")

print("\nSelect team(s) for user (for non-admin users):")
print("1. new_branch - ทีมสาขาใหม่")
print("2. legal      - ทีมกฎหมาย")
print("3. srd        - ทีม SRD")
print("4. scm        - ทีม SCM")
print("5. all        - All teams")
print("6. none       - No teams (admin doesn't need teams)")

team_choice = input("Choose team(s) (comma-separated, e.g., 1,2) [default: none]: ").strip()

teams = []
if team_choice and team_choice != "6":
    if team_choice == "5":
        teams = ["new_branch", "legal", "srd", "scm"]
    else:
        team_map = {"1": "new_branch", "2": "legal", "3": "srd", "4": "scm"}
        for choice in team_choice.split(","):
            choice = choice.strip()
            if choice in team_map:
                teams.append(team_map[choice])

team_role = "viewer"
if teams:
    print("\nSelect role in team(s):")
    print("1. viewer  - Read-only")
    print("2. editor  - Can edit")
    print("3. manager - Full team access")
    role_choice = input("Choose (1-3) [default: 2]: ").strip() or "2"
    role_map = {"1": "viewer", "2": "editor", "3": "manager"}
    team_role = role_map.get(role_choice, "editor")

print("\n" + "=" * 60)
print("Summary:")
print(f"  Email: {email}")
print(f"  Name: {name}")
print(f"  User Level: {user_level}")
if teams:
    print(f"  Teams: {', '.join(teams)}")
    print(f"  Role: {team_role}")
else:
    print(f"  Teams: (none - {user_level} has access to all)")
print("=" * 60)

confirm = input("\nCreate this user? (y/n): ").strip().lower()
if confirm != 'y':
    print("Cancelled.")
    sys.exit(0)

# Create user
user_id = str(uuid.uuid4())
now = datetime.now().isoformat()

user_data = {
    'user_id': user_id,
    'email': email,
    'name': name,
    'user_level': user_level,
    'is_active': True,
    'created_at': now,
    'updated_at': now,
    'last_login': None
}

try:
    # Insert user
    table_id = f"{PROJECT_ID}.{DATASET_ID}.users"
    table = client.get_table(table_id)
    errors = client.insert_rows_json(table, [user_data])

    if errors:
        print(f"❌ Failed to create user: {errors}")
        sys.exit(1)

    print(f"✅ User created with ID: {user_id}")

    # Add teams
    if teams:
        team_data = []
        for team_name in teams:
            team_data.append({
                'user_team_id': str(uuid.uuid4()),
                'user_id': user_id,
                'team_name': team_name,
                'role': team_role,
                'created_at': now,
                'created_by': 'system'
            })

        table_id = f"{PROJECT_ID}.{DATASET_ID}.user_teams"
        table = client.get_table(table_id)
        errors = client.insert_rows_json(table, team_data)

        if errors:
            print(f"⚠️  Warning: Failed to add teams: {errors}")
        else:
            print(f"✅ Added user to {len(teams)} team(s)")

    print("\n" + "=" * 60)
    print("✅ Test user created successfully!")
    print("\nYou can now:")
    print("1. Start the app: ./scripts/run_local.sh")
    print("2. Visit: http://localhost:8000/login")
    print(f"3. Login with: {email}")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error creating user: {e}")
    sys.exit(1)
