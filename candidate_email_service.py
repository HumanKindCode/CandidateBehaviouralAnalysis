# @author: Ramasubramanya Mysore Sheshadri | MS student at RMIT University

import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# Google Sheets connection setup
def init_gspread_connection():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(".streamlit/behavioral-forms-90a681513583.json", scope)
    client = gspread.authorize(creds)
    return client

# Insert data into Google Sheets
def insert_data_into_sheet(client, spreadsheet_id, worksheet_name, data):
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    sheet.append_row(data)

# Email sending function with Google Sheets integration
def send_email(subject, message, recipient_emails, client, spreadsheet_id, worksheet_name):
    sender_email = "humankind.au@gmail.com"
    sender_password = "yfvh vnzd rcfn mskj"  # Use an environment variable or secure method to store this
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Common port for email sending

    # Set up server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Start TLS encryption
    server.login(sender_email, sender_password)

    email_timestamps = []  # To store timestamps of sent emails

    # Create and send email
    for recipient_email in recipient_emails:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        body = MIMEText(message, "plain")
        msg.attach(body)

        # Send email
        server.send_message(msg)
        email_timestamps.append((recipient_email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    server.quit()

    # Insert data into Google Sheets
    for index, (email, timestamp) in enumerate(email_timestamps, start=1):
        # Prepare the data for insertion: index, timestamp, email
        data = [index, email, timestamp.split(' ')[0], timestamp.split(' ')[1]]
        insert_data_into_sheet(client, spreadsheet_id, worksheet_name, data)

    return len(email_timestamps)  # Return the number of emails sent

client = init_gspread_connection()
spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
worksheet_name = "Sheet2"
present_date = datetime.now()
deadline_date = present_date + timedelta(days=1)
formatted_deadline_date = deadline_date.strftime('%B %d, %Y')

# Streamlit UI setup
st.title("Send Emails")

default_email_subject = "Invitation to the Next Phase of the Selection Process"
default_email_text = f"""
Dear Candidate,

I hope this email finds you well. I am Tanya Brown, the hiring manager for the at our company. I am pleased to inform you that after reviewing your application and initial screening results, we are interested in moving forward to the next phase of our selection process.

This next step is designed to help us understand our candidates better, focusing on behavioral aspects that are crucial to the role. To this end, we have prepared an assessment that we believe will give us deeper insight into your approach to work, decision-making, and interpersonal relationships.

Please access the assessment through the following link: https://candidatebehaviouralanalysis.streamlit.app/

We kindly ask you to complete the assessment by {formatted_deadline_date}. It should take approximately 10 minutes to complete. Rest assured, your responses will be kept confidential and used solely for the purpose of this hiring process.

Should you have any questions or require further clarification, please do not hesitate to contact me directly via email or phone at [Your Contact Information].

We are looking forward to your participation in this next phase and are excited about the potential of having you join our team.

Thank you for your time and consideration.

Warm regards,

[Tanya Brown]
[Your Position]
[Your Contact Information]

"""
# Inputs
recipient_emails = st.text_input("Recipient Email(s)", help="Use commas to separate multiple emails")
subject = st.text_input("Subject", value=default_email_subject)
message = st.text_area("Message", value=default_email_text)

# Send button
if st.button("Send Email"):
    recipient_emails_list = [email.strip() for email in recipient_emails.split(",")]
    emails_sent = send_email(subject, message, recipient_emails_list, client, spreadsheet_id, worksheet_name)
    if emails_sent > 0:
        st.success(f"Email sent to {emails_sent} recipients!")
    else:
        st.error("Failed to send emails.")
