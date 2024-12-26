import streamlit as st
from auth import init_auth_db, authenticate_user, register_user, get_user_role, change_password
from database import init_db, get_projects, update_project, add_project, get_team_members, add_team_member
from github_integration import log_issue_to_github
from notifications import schedule_reminders
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialize databases
init_db()
init_auth_db()

# Sidebar Authentication
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # Login Callback
    def login_callback(email, password):
        if authenticate_user(email, password):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["role"] = get_user_role(email)
            st.sidebar.success(f"Welcome, {email}!")
        else:
            st.sidebar.error("Invalid email or password.")

    # Sidebar Login
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    st.sidebar.button("Login", on_click=lambda: login_callback(email, password))

else:
    # Main App Content After Login
    st.sidebar.title("Navigation")
    tabs = st.sidebar.radio("Go To", ["Dashboard", "Projects", "GitHub Issues", "Reminders", "Team"])

    # Admin Options for Password Change
    if st.session_state["email"] == "admin@ic.ac.uk":
        st.sidebar.title("Admin Options")
        new_password = st.sidebar.text_input("New Password", type="password")
        if st.sidebar.button("Change Password"):
            change_password("admin@ic.ac.uk", new_password)
            st.sidebar.success("Password updated!")

    # Dashboard
    if tabs == "Dashboard":
        st.title("Welcome to CHEPI Project Management!")
        projects = get_projects()

        if projects:
            project_df = pd.DataFrame(projects)
            st.subheader("Project Progress Overview")
            progress_chart = px.bar(project_df, x="name", y="progress", title="Project Progress")
            st.plotly_chart(progress_chart)

            st.subheader("Project Status Distribution")
            status_chart = px.pie(project_df, names="status", title="Project Status")
            st.plotly_chart(status_chart)
        else:
            st.write("No projects found. Add new projects in the Projects tab.")

    # Projects
    elif tabs == "Projects":
        st.title("Manage Projects")
        projects = get_projects()

        if projects:
            for project in projects:
                with st.expander(f"{project['name']}"):
                    st.write(f"Description: {project['description']}")
                    st.write(f"Deadline: {project['deadline']}")
                    st.write(f"Progress: {project['progress']}%")
                    st.write(f"Status: {project['status']}")

                    name = st.text_input("Name", value=project["name"], key=f"name_{project['id']}")
                    description = st.text_area("Description", value=project["description"], key=f"desc_{project['id']}")
                    deadline = st.date_input("Deadline", value=project["deadline"], key=f"deadline_{project['id']}")
                    progress = st.slider("Progress", 0, 100, value=project["progress"], key=f"progress_{project['id']}")
                    status = st.selectbox(
                        "Status", ["Pending", "In Progress", "Completed"],
                        index=["Pending", "In Progress", "Completed"].index(project["status"]),
                        key=f"status_{project['id']}"
                    )

                    if st.button("Save Changes", key=f"save_{project['id']}"):
                        update_project(project["id"], name, description, deadline, progress, status)
                        st.success(f"Updated project: {project['name']}")
        else:
            st.write("No projects found. Use the form below to add one.")

        st.subheader("Add a New Project")
        name = st.text_input("Project Name")
        description = st.text_area("Description")
        deadline = st.date_input("Deadline")
        if st.button("Add Project"):
            add_project(name, description, deadline)
            st.success("Project added successfully!")

    # GitHub Issues
    elif tabs == "GitHub Issues":
        st.title("GitHub Issue Tracker")
        token = st.text_input("GitHub Token", type="password")
        repo_name = st.text_input("Repository Name (e.g., username/repo)")
        projects = get_projects()
        issue_project = st.selectbox("Select Project", [p["name"] for p in projects])
        issue_description = st.text_area("Issue Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        if st.button("Log Issue"):
            try:
                log_issue_to_github(token, repo_name, issue_project, issue_description, priority)
                st.success("GitHub issue logged successfully!")
            except Exception as e:
                st.error(f"Failed to create issue: {str(e)}")

    # Reminders
    elif tabs == "Reminders":
        st.title("Set Reminders")
        recipient = st.text_input("Recipient Email")
        projects = get_projects()
        selected_project = st.selectbox("Select Project", [p["name"] for p in projects])
        date = st.date_input("Date")
        time = st.time_input("Time")
        message = st.text_area("Reminder Message")
        if st.button("Set Reminder"):
            schedule_reminders(recipient, message, datetime.combine(date, time))
            st.success("Reminder scheduled successfully!")

    # Team
    elif tabs == "Team":
        st.title("Team Overview")
        members = get_team_members()
        st.subheader("Current Team Members")
        st.table(pd.DataFrame(members))
        st.subheader("Add New Team Member")
        name = st.text_input("Member Name")
        email = st.text_input("Member Email")
        if st.button("Add Member"):
            add_team_member(name, email)
            st.success(f"Added team member: {name}")
