import requests
from datetime import datetime, timedelta

# Constants for Asana API
ASANA_BASE_URL = "https://app.asana.com/api/1.0"
ACCESS_TOKEN = "2/1208780346696825/1208823852542223:0562c26eddedc7b241220dabd47b7af8"  # Replace with your Asana API token

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Utility Functions
def get_section_id(project_id, section_name):
    """Fetch the section ID for a given section name."""
    response = requests.get(f"{ASANA_BASE_URL}/projects/{project_id}/sections", headers=HEADERS)
    response.raise_for_status()
    sections = response.json().get("data", [])
    for section in sections:
        if section.get("name") == section_name:
            return section.get("gid")
    raise ValueError(f"Section '{section_name}' not found in project {project_id}.")

def move_task_to_section(task_id, project_id, section_id):
    """Move a task to a specific section."""
    payload = {
        "data": {
            "project": project_id,  # Ensure the task is added to the correct project
            "section": section_id
        }
    }
    response = requests.post(f"{ASANA_BASE_URL}/tasks/{task_id}/addProject", headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Task {task_id} successfully moved to 'In Progress' section.")
    else:
        print(f"Failed to move task {task_id}. Response: {response.text}")

def update_task_due_date(task_id, new_due_date):
    """Update the due date of a task."""
    payload = {"data": {"due_on": new_due_date}}
    response = requests.put(f"{ASANA_BASE_URL}/tasks/{task_id}", headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Task {task_id} updated with new due date: {new_due_date}")
    else:
        print(f"Failed to update task {task_id}. Response: {response.text}")

def adjust_due_dates_in_progress(project_id, high_priority_task_id, excluded_task_id):
    """Adjust due dates for all tasks in 'In Progress' when a high-priority task is moved."""
    # Get all tasks in the project
    response = requests.get(f"{ASANA_BASE_URL}/projects/{project_id}/tasks", headers=HEADERS)
    response.raise_for_status()
    tasks = response.json().get("data", [])

    for task in tasks:
        task_id = task["gid"]
        
        # Skip the high-priority task and any specific task we want to exclude
        if task_id == high_priority_task_id or task_id == excluded_task_id:
            continue

        # Get task details
        task_details = requests.get(f"{ASANA_BASE_URL}/tasks/{task_id}", headers=HEADERS).json().get("data")
        memberships = task_details.get("memberships", [])

        for membership in memberships:
            section = membership.get("section", {}).get("name")
            if section == "In Progress":  # Only modify tasks in the "In Progress" section
                current_due_date = task_details.get("due_on")
                if current_due_date:
                    # Extend the due date by 2 days
                    new_due_date = (datetime.strptime(current_due_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
                    update_task_due_date(task_id, new_due_date)

# Main Functionality
def main():
    project_id = "1208780347001262"  # Replace with your project ID
    task_id_to_move = "1208780347001281"  # Replace with the ID of the task you want to move
    excluded_task_id = "1208780347001281"  # Replace with the ID of the task to exclude from due date update
    high_priority = True  # Set True if the task being moved is high-priority

    # Step 1: Fetch section ID for 'In Progress'
    print("Fetching section ID for 'In Progress'...")
    in_progress_section_id = get_section_id(project_id, "In Progress")

    # Step 2: Move the task to the 'In Progress' section
    print(f"Moving task {task_id_to_move} to 'In Progress' section...")
    move_task_to_section(task_id_to_move, project_id, in_progress_section_id)

    # Step 3: Adjust other tasks in 'In Progress' if the task is high-priority
    if high_priority:
        print("Task is high-priority. Adjusting due dates of other tasks in 'In Progress'...")
        adjust_due_dates_in_progress(project_id, task_id_to_move, excluded_task_id)
    else:
        print("Task is not high-priority. No further adjustments needed.")

if __name__ == "__main__":
    main()
