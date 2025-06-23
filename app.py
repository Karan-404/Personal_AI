# Cyber Security Course Advisor via AWS Bedrock
# Author: Cyrus Gao, extended by Xiang Li
# Updated: May 2025

import streamlit as st
import json
import boto3
from datetime import datetime
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import csv
import io
import sqlite3
import pdfplumber
import time

# === AWS Configuration === #
REGION = "us-east-1"
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
IDENTITY_POOL_ID = "us-east-1:7771aae7-be2c-4496-a582-615af64292cf"
USER_POOL_ID = "us-east-1_koPKi1lPU"
APP_CLIENT_ID = "3h7m15971bnfah362dldub1u2p"

# Load credentials with safe fallback
load_dotenv()
DEFAULT_USERNAME = os.getenv("RMIT_USERNAME")
DEFAULT_PASSWORD = os.getenv("RMIT_PASSWORD")


def get_credentials(username=None, password=None):
    """Get AWS credentials with better error handling"""
    try:
        if username is None or password is None:
            username = DEFAULT_USERNAME
            password = DEFAULT_PASSWORD

        idp_client = boto3.client("cognito-idp", region_name=REGION)
        response = idp_client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=APP_CLIENT_ID,
        )
        id_token = response["AuthenticationResult"]["IdToken"]

        identity_client = boto3.client("cognito-identity", region_name=REGION)
        identity_response = identity_client.get_id(
            IdentityPoolId=IDENTITY_POOL_ID,
            Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
        )

        creds_response = identity_client.get_credentials_for_identity(
            IdentityId=identity_response["IdentityId"],
            Logins={f"cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}": id_token},
        )

        return creds_response["Credentials"]
    
    except Exception as e:
        print(f"Authentication error: {e}")  # For debugging
        raise e

def build_prompt(courses, user_question, structure=None):
    course_dict = {c["title"]: c for c in courses}

    structure_text = ""
    if structure and "recommended_courses" in structure:
        structure_text += "### Recommended Study Plan by Year:\n"
        for year, course_titles in structure["recommended_courses"].items():
            structure_text += f"**{year.replace('_', ' ').title()}**:\n"
            for title in course_titles:
                course = course_dict.get(title)
                if course:
                    structure_text += f"- {title} ({course['course_code']})\n"
                else:
                    structure_text += f"- {title} (not found in course list)\n"
            structure_text += "\n"

    course_list = []
    for course in courses:
        title = course.get("title", "Untitled")
        code = course.get("course_code", "N/A")
        desc = course.get("description", "No description available.")
        course_type = course.get("course_type", "N/A")
        minor = course.get("minor_track", [])
        minor_info = f", Minor: {minor[0]}" if minor else ""
        course_text = f"- {title} ({code}): {desc}\n  Type: {course_type}{minor_info}"
        course_list.append(course_text)
    full_course_context = "\n".join(course_list)

    prompt = (
        "You are a helpful assistant that supports students in selecting courses from the "
        "Bachelor of Cyber Security program at RMIT (codes BP355/BP356). "
        "Recommend only from the official course list. Each course is categorized as core, capstone, minor, or elective. "
        "Use the recommended structure to suggest suitable courses based on study year and interest.\n\n"
        + structure_text
        + "\n### All Available Courses:\n"
        + full_course_context
        + "\n\nUser:\n" + user_question
    )
    return prompt

def extract_text_from_pdfs(pdf_files):
    all_text = []
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text.strip())
        except Exception as e:
            all_text.append(f"[Error reading file {pdf_file.name}: {str(e)}]")
    return "\n\n".join(all_text)

def convert_pdf_to_json(uploaded_files):
    pdf_data = {}
    for i, f in enumerate(uploaded_files, start=1):
        try:
            with pdfplumber.open(f) as pdf:
                pages = [page.extract_text().strip() for page in pdf.pages if page.extract_text()]
                pdf_data[f"pdf_{i}"] = pages
        except Exception as e:
            pdf_data[f"pdf_{i}"] = [f"Error reading file {f.name}: {str(e)}"]
    return pdf_data

def invoke_bedrock(prompt_text, username=None, password=None, max_tokens=640, temperature=0.3, top_p=0.9):
    credentials = get_credentials(username, password)

    bedrock_runtime = boto3.client(
        "bedrock-runtime",
        region_name=REGION,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"],
    )

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [{"role": "user", "content": prompt_text}]
    }

    response = bedrock_runtime.invoke_model(
        body=json.dumps(payload),
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

# === Streamlit UI === #
st.set_page_config(page_title="RMIT Course Advisor", layout="wide")
st.markdown("## 🎓 RMIT Course Advisor")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""

# === Login UI ===
if not st.session_state.logged_in:
    # Create a centered login container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header with RMIT branding
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #E40613; margin-bottom: 0.5rem;">🎓 RMIT Course Advisor</h1>
            <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
                Your AI-powered guide to Bachelor of Cyber Security courses
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form with better styling
        with st.container():
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 10px; border: 1px solid #e9ecef;">
            """, unsafe_allow_html=True)
            
            st.markdown("### 🔐 Login to Continue")
            st.markdown("Sign in with your RMIT aws credentials or use guest access")
            
            with st.form("login_form", clear_on_submit=False):
                # Username input
                username_input = st.text_input(
                    "👤 Username", 
                    placeholder="Enter your RMIT username",
                    help="Use your RMIT student ID or email"
                )
                
                # Password input
                password_input = st.text_input(
                    "🔒 Password", 
                    type="password", 
                    placeholder="Enter your password",
                    help="Your RMIT account password"
                )
                
                # Login buttons with better layout
                st.markdown("<br>", unsafe_allow_html=True)
                col_login1, col_login2 = st.columns(2)
                
                with col_login1:
                    submitted = st.form_submit_button(
                        "🔑 Login", 
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_login2:
                    guest_login = st.form_submit_button(
                        "👤 Guest Access", 
                        use_container_width=True,
                        help="Access with limited demo functionality"
                    )
                
                # Login logic with better error handling
                if submitted:
                    if not username_input.strip() or not password_input.strip():
                        st.warning("⚠️ Please enter both username and password.")
                    else:
                        with st.spinner("🔄 Authenticating..."):
                            try:
                                get_credentials(username_input, password_input)
                                st.session_state.logged_in = True
                                st.session_state.username = username_input
                                st.session_state.password = password_input
                                st.success("✅ Login successful! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                error_msg = str(e)
                                if "NotAuthorizedException" in error_msg:
                                    st.error("❌ Invalid username or password")
                                    st.info("💡 Please check your RMIT credentials or try Guest Access")
                                elif "UserNotFoundException" in error_msg:
                                    st.error("❌ User not found")
                                    st.info("💡 Please check your username or try Guest Access")
                                else:
                                    st.error(f"❌ Login failed: {error_msg}")
                                    st.info("💡 Please try Guest Access if the problem persists")
                
                if guest_login:
                    with st.spinner("🔄 Setting up guest access..."):
                        try:
                            # Check if default credentials are set
                            if not DEFAULT_USERNAME or not DEFAULT_PASSWORD:
                                st.error("❌ Guest credentials not configured")
                                st.info("💡 Please contact administrator to set up guest access")
                            else:
                                get_credentials(DEFAULT_USERNAME, DEFAULT_PASSWORD)
                                st.session_state.logged_in = True
                                st.session_state.username = DEFAULT_USERNAME  # Use actual guest username here
                                st.session_state.password = DEFAULT_PASSWORD
                                st.success("✅ Guest access granted! Welcome!")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "NotAuthorizedException" in error_msg:
                                st.error("❌ Guest credentials are invalid")
                                st.info("💡 Please contact administrator to update guest credentials")
                            else:
                                st.error(f"❌ Guest login failed: {error_msg}")
                                st.info("💡 Please contact support if this issue persists")

            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional information
            st.markdown("---")
            
            # Feature highlights
            with st.expander("✨ What you can do with RMIT Course Advisor", expanded=False):
                st.markdown("""
                **🎯 Personalized Course Recommendations**
                - Get AI-powered course suggestions based on your interests
                - Understand prerequisites and course pathways
                
                **📚 Comprehensive Course Database**
                - Access detailed information about all Cyber Security courses
                - Filter courses by type, level, and specialization
                
                **🤖 Intelligent Q&A**
                - Ask questions in natural language
                - Get detailed explanations and guidance
                
                **📄 Document Analysis**
                - Upload PDFs for course information extraction
                - Convert documents to structured data
                """)
            
            # Support information
            with st.expander("🆘 Need Help?", expanded=False):
                st.markdown("""
                **For Students:**
                - Use your regular RMIT login credentials
                - If you don't have access, try Guest mode for a demo
                
                **Technical Issues:**
                - Clear your browser cache and try again
                - Ensure you have a stable internet connection
                - Contact IT support if problems persist
                
                **About Guest Access:**
                - Limited to demo functionality
                - Uses sample course data
                - Perfect for exploring the system
                """)

else:
    # === Main App Interface ===
    # Header with user info and logout
    st.markdown("""
    <div style="background: linear-gradient(90deg, #E40613 0%, #FF6B7A 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        display_name = st.session_state.username
        if display_name == "Guest User":
            st.markdown(f"<h3 style='color: white; margin: 0;'>🎓 Welcome back, {display_name}! 👋</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFE4E6; margin: 0; font-size: 0.9rem;'>You're using guest access with demo data</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h3 style='color: white; margin: 0;'>🎓 Welcome Guest! 👋</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #FFE4E6; margin: 0; font-size: 0.9rem;'>Ready to explore your course options?</p>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True, help="Sign out and return to login"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.password = ""
            st.success("👋 Logged out successfully!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # === Step 1: Data Input ===
    st.subheader("📂 Step 1: Choose Data Source")
    data_source = st.radio(
        "Select your data source:",
        ["📄 Upload Files", "🗄️ Use Database", "📝 Extract from PDFs"],
        horizontal=True
    )

    uploaded_courses_json = uploaded_structure_json = None
    uploaded_courses_csv = uploaded_structure_csv = None
    uploaded_pdfs = None

    if data_source == "📄 Upload Files":
        upload_format = st.selectbox(
            "Choose file format:",
            ["JSON files", "CSV files"]
        )
        
        if upload_format == "JSON files":
            col1, col2 = st.columns(2)
            with col1:
                uploaded_courses_json = st.file_uploader("📋 Courses Data", type=["json"], key="courses_json")
            with col2:
                uploaded_structure_json = st.file_uploader("🏗️ Program Structure", type=["json"], key="structure_json")
        else:
            col1, col2 = st.columns(2)
            with col1:
                uploaded_courses_csv = st.file_uploader("📋 Courses Data", type=["csv"], key="courses_csv")
            with col2:
                uploaded_structure_csv = st.file_uploader("🏗️ Program Structure", type=["csv"], key="structure_csv")
    
    elif data_source == "📝 Extract from PDFs":
        uploaded_pdfs = st.file_uploader("📑 Upload PDF Files", type=["pdf"], accept_multiple_files=True, key="pdfs")
        
        # Add PDF to JSON conversion with download button
        if uploaded_pdfs:
            if st.button("📄 Convert PDF to JSON"):
                with st.spinner("Converting PDFs to JSON..."):
                    pdf_json = convert_pdf_to_json(uploaded_pdfs)
                    st.json(pdf_json)
                    
                    # Create download button
                    json_string = json.dumps(pdf_json, indent=2)
                    st.download_button(
                        label="💾 Download PDF as JSON",
                        data=json_string,
                        file_name="converted_pdf_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
                    st.success("✅ PDF converted to JSON successfully!")
    
    elif data_source == "🗄️ Use Database":
        with st.expander("⚙️ Database Information", expanded=True):
            try:
                conn = sqlite3.connect("extracted_data.db")
                cursor = conn.cursor()
                
                # Get tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables] if tables else []
                
                if table_names:
                    st.info(f"📊 **Available Tables:** {', '.join(table_names)}")
                    
                    # Find course table
                    possible_course_tables = ['courses', 'course', 'course_data', 'extracted_courses']
                    course_table = None
                    for possible_table in possible_course_tables:
                        if possible_table in table_names:
                            course_table = possible_table
                            break
                    
                    # If not found, just pick the first table
                    if not course_table and table_names:
                        course_table = table_names[0]
                    
                    if course_table:
                        # Show rows count
                        cursor.execute(f"SELECT COUNT(*) FROM {course_table}")
                        row_count = cursor.fetchone()[0]
                        st.success(f"📋 **Main Table:** {course_table} ({row_count} records)")
                
                conn.close()
                
            except Exception as e:
                st.warning(f"Could not read database information: {e}")

    st.divider()

    # === Step 2: Ask Question ===
    st.subheader("💬 Step 2: Ask Your Question")
    user_question = st.text_area(
        "What would you like to know?",
        placeholder="e.g., I'm a second-year student interested in digital forensics and blockchain. What courses should I take?",
        height=100
    )

    # === Get Advice Button ===
    if st.button("🎯 Get Course Advice", type="primary", use_container_width=True):
        if not user_question.strip():
            st.warning("⚠️ Please enter a question.")
        else:
            try:
                with st.spinner("🔍 Generating personalized advice..."):
                    # Process based on data source
                    if data_source == "📄 Upload Files":
                        if upload_format == "JSON files":
                            if not uploaded_courses_json or not uploaded_structure_json:
                                st.warning("⚠️ Please upload both JSON files.")
                                st.stop()
                            courses = json.load(uploaded_courses_json)
                            structure = json.load(uploaded_structure_json)
                            prompt = build_prompt(courses, user_question, structure)
                        else:  # CSV files
                            if not uploaded_courses_csv or not uploaded_structure_csv:
                                st.warning("⚠️ Please upload both CSV files.")
                                st.stop()
                            courses = list(csv.DictReader(io.StringIO(uploaded_courses_csv.getvalue().decode("utf-8"))))
                            structure = list(csv.DictReader(io.StringIO(uploaded_structure_csv.getvalue().decode("utf-8"))))
                            prompt = build_prompt(courses, user_question, structure)
                    
                    elif data_source == "📝 Extract from PDFs":
                        if not uploaded_pdfs:
                            st.warning("⚠️ Please upload at least one PDF file.")
                            st.stop()
                        extracted_text = extract_text_from_pdfs(uploaded_pdfs)
                        prompt = (
                            "You are a course advisor. The following is extracted from official course documents:\n\n"
                            + extracted_text +
                            "\n\nPlease answer the following question based on this information:\n"
                            + user_question
                        )
                    
                    else:  # Database
                        try:
                            conn = sqlite3.connect("extracted_data.db")
                            cursor = conn.cursor()
                            
                            # Check what tables exist in the database
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                            tables = cursor.fetchall()
                            
                            if not tables:
                                st.warning("⚠️ No tables found in the database.")
                                st.stop()
                            
                            # Attempt to find the course table
                            table_names = [table[0] for table in tables]
                            possible_course_tables = ['courses', 'course', 'course_data', 'extracted_courses']
                            course_table = None
                            
                            for possible_table in possible_course_tables:
                                if possible_table in table_names:
                                    course_table = possible_table
                                    break
                            
                            if not course_table:
                                # Use first available table
                                course_table = table_names[0]
                                st.info(f"Using table: {course_table}")
                            

                            # Get table schema to understand columns
                            cursor.execute(f"PRAGMA table_info({course_table})")
                            columns = cursor.fetchall()
                            column_names = [col[1] for col in columns]
                            
                            # Build query based on available columns
                            select_columns = []
                            if 'title' in column_names:
                                select_columns.append('title')
                            elif 'name' in column_names:
                                select_columns.append('name as title')
                            else:
                                select_columns.append("'Unknown' as title")
                                
                            if 'course_code' in column_names:
                                select_columns.append('course_code')
                            elif 'code' in column_names:
                                select_columns.append('code as course_code')
                            else:
                                select_columns.append("'N/A' as course_code")
                                
                            if 'description' in column_names:
                                select_columns.append('description')
                            else:
                                select_columns.append("'No description available' as description")
                                
                            if 'course_type' in column_names:
                                select_columns.append('course_type')
                            elif 'type' in column_names:
                                select_columns.append('type as course_type')
                            else:
                                select_columns.append("'General' as course_type")
                                
                            if 'minor_track' in column_names:
                                select_columns.append('minor_track')
                            else:
                                select_columns.append("'[]' as minor_track")
                
                            # Query without filters
                            query = f"SELECT {', '.join(select_columns)} FROM {course_table}"
                            cursor.execute(query)
                            courses_data = cursor.fetchall()
                            conn.close()

                            if not courses_data:
                                st.warning("⚠️ No courses found in the database.")
                                st.stop()
                
                            # Format course data as text
                            course_list = []
                            for c in courses_data:
                                title = c[0] if c[0] else "Unknown"
                                code = c[1] if c[1] else "N/A"
                                desc = c[2] if c[2] else "No description available"
                                course_type = c[3] if c[3] else "General"
                                minor_track = c[4] if c[4] else "[]"
                                
                                course_text = f"- {title} ({code}): {desc}\n  Type: {course_type}, Track: {minor_track}"
                                course_list.append(course_text)
                        
                            course_text = "\n".join(course_list)
                            
                        except sqlite3.Error as db_error:
                            st.error(f"Database error: {str(db_error)}")
                            st.info("Please check if the database file exists and has the correct structure.")
                            st.stop()
                        except Exception as general_error:
                            st.error(f"Error accessing database: {str(general_error)}")
                            st.stop()
                        
                        # Simple prompt format
                        prompt = f"You're a course advisor for RMIT students. Here is the course content:\n\n{course_text}\n\nUser asks:\n{user_question}"

                    # Get advice from Claude
                    answer = invoke_bedrock(prompt, st.session_state.username, st.session_state.password)
                    
                    # Display results
                    st.success("✅ Advice Generated Successfully!")
                    st.markdown("### 🤖 Course Recommendation")
                    st.markdown(answer)

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
