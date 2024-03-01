import streamlit as st

st.header("Candidate Psyche Analysis")
st.markdown("### Candidate Email Service: http://13.239.116.255/")
st.markdown("""



    Database Connection Procedure:

    Step 1: Download DBeaver
    - Visit the DBeaver official website: [https://dbeaver.io/download/](https://dbeaver.io/download/)
    - Choose the edition you want to download. For most users, the Community Edition is sufficient and free to use.
    - Select the installer based on your operating system (Windows, macOS, Linux).
    - Download the installer.

    Step 2: Install DBeaver
    - **Windows**: Run the downloaded installer and follow the on-screen instructions.
    - **macOS**: Open the `.dmg` file and drag the DBeaver application into your Applications folder.
    - **Linux**: The installation process can vary depending on the distribution. For Debian-based distributions, you can often install DBeaver from the downloaded `.deb` package using your package manager.

    Step 3: Open DBeaver and Start a New Connection
    - Open DBeaver.
    - On the welcome screen, you’ll see an option to create a new connection. If you don't see the welcome screen, click on "Database" in the top menu and select "New Database Connection."

    Step 4: Configure the Connection
    - In the "New Connection" wizard, choose "PostgreSQL" as the database you want to connect to. Click "Next."
    - In the connection settings, fill in the details with the information you provided:
        - **Host**: `database-1.clm0wcc6k54c.ap-southeast-2.rds.amazonaws.com`
        - **Port**: PostgreSQL default port is `5432`. Unless specified otherwise, use this port.
        - **Database**: `CandidPersonaAnalysis`
        - **User**: `mike`
        - **Password**: Click on the "Edit" button next to the password field and enter `HumanKind25`.
    - (Optional) Click on "Test Connection" to verify that DBeaver can connect to your database using the provided details. You might need to install drivers; DBeaver will prompt you to download them if necessary. Accept the download, and after the drivers are installed, try testing the connection again.
    - Once the connection is successfully tested, click "Finish" to create the connection.

    Step 5: Explore Your Database
    - After the connection is established, you will see your database schema on the left side panel. You can expand the schema to view tables, execute SQL queries, and perform other database operations.
""", unsafe_allow_html=True)
