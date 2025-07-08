import streamlit as st
import mysql.connector as msc
import random
from datetime import datetime

# Database connections
@st.cache_resource
def get_db_connections():
    sqldata1 = msc.connect(
        host="localhost",
        user="root",
        password="idiosyncratic",
        database="doctors"
    )
    csr1 = sqldata1.cursor()

    sqldata2 = msc.connect(
        host="localhost",
        user="root",
        password="idiosyncratic",
        database="patients"
    )
    csr2 = sqldata2.cursor()
    return csr1, csr2, sqldata1, sqldata2

csr1, csr2, sqldata1, sqldata2 = get_db_connections()


class Appointment:
    def __init__(self):
        st.title("🏥 Doctor-Patient Appointment System")
        st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2005/2005973.png", width=100)

        self.name = ""
        self.app_id = ""
        self.age = ""
        self.address = ""
        self.city = ""
        self.state = ""
        self.sex = ""
        self.doctor_appointed = ""
        self.password = ""

        option = st.sidebar.radio("Select User Type", ["Doctor", "Patient"])

        if option == "Doctor":
            self.doctor_menu()
        elif option == "Patient":
            self.patient_menu()

    def doctor_menu(self):
        self.doctor_login_success = False
        self.doctor_name = ""
        self.doctor_email = ""
    
        st.header("👨‍⚕️ Doctors Interface")
        tab1, tab2 = st.tabs(["Register", "Login"])

        with tab1:
            with st.form("doctor_registration"):
                st.subheader("New Doctor Registration")
                self.name = st.text_input("Name")
                self.specialisation = st.text_input("Specialization")
                self.sex = st.radio("Sex", ["M", "F"])
                self.experienced_work_place = st.text_input("Previous Working Hospitals/Institutions")
                self.age = st.number_input("Age", min_value=18, max_value=100)
                self.experience_years = st.text_input("Working Experience")
                self.contact_number = st.text_input("Contact number")
                email = st.text_input("Email ID")
                password = st.text_input("Password", type="password")
    
                if st.form_submit_button("Register"):
                    csr1.execute(
                        'INSERT INTO doctorslist VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                        (self.name, self.specialisation, self.sex,
                         self.experienced_work_place, self.age, self.experience_years,
                         self.contact_number, email, password)
                    )
                    sqldata1.commit()
                    st.success(f"Dr. {self.name} registered successfully.")
                    st.info("Your Login Username will be your Email Address.")
    
        with tab2:
            st.subheader("Doctor Login")
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
    
            if st.button("Login"):
                csr1.execute("SELECT * FROM doctorslist WHERE email = %s AND password = %s",
                             (login_email, login_password))
                doctor = csr1.fetchone()
                if doctor:
                    self.doctor_name = doctor[0]
                    self.doctor_email = doctor[7]
                    self.doctor_login_success = True
                    st.success(f"Welcome, Dr. {doctor[0]}!")
                else:
                    st.error("Invalid credentials.")
    
        # === Doctor Dashboard ===

        if self.doctor_login_success:
            st.header("📋 Doctor Dashboard")
    
            # Show all patients assigned to this doctor
            csr2.execute("""
                SELECT app_id, name, age, sex, city, symptom, duration, app_date, app_time, remarks, prescription
                FROM patientlist
                WHERE doctor_appointed = %s
                ORDER BY app_date IS NULL, app_date, app_time
            """, (self.doctor_name,))
            appointments = csr2.fetchall()
    
            if appointments:
                for appt in appointments:
                    appt_id = appt[0]
                    with st.expander(f"{appt[1]} | {appt[7] or 'Not yet booked'} at {appt[8] or '—'}"):
                        st.markdown(f"**Appointment ID:** {appt[0]}")
                        st.markdown(f"**Name:** {appt[1]}")
                        st.markdown(f"**Age / Sex / City:** {appt[2]} / {appt[3]} / {appt[4]}")
                        st.markdown(f"**Symptoms:** {appt[5]}")
                        st.markdown(f"**Duration:** {appt[6]}")
                        st.markdown(f"**Date & Time:** {appt[7] or 'Not set'} at {appt[8] or 'Not set'}")
    
                        # Maintain values using unique keys
                        remarks_key = f"remarks_{appt_id}"
                        presc_key = f"presc_{appt_id}"
                        save_key = f"save_{appt_id}"
    
                        remarks = st.text_area("📝 Remarks", appt[9] or "", key=remarks_key)
                        prescription = st.text_area("💊 Prescription", appt[10] or "", key=presc_key)
    
                        if st.button("💾 Save", key=save_key):
                            csr2.execute("""
                                UPDATE patientlist 
                                SET remarks = %s, prescription = %s 
                                WHERE app_id = %s
                            """, (remarks, prescription, appt_id))
                            sqldata2.commit()
                            st.success("✅ Saved successfully!")
    
            else:
                st.info("No patients have been assigned yet.")




    def patient_menu(self):
        st.header("👨‍⚕️ Patient Appointment System")
        menu = st.sidebar.selectbox("Menu", [
            "New Appointment", "Existing Patient",
            "Reports/Prescription", "Expert Doctors Panel"
        ])

        if menu == "New Appointment":
            self.register_patient()
        elif menu == "Existing Patient":
            self.login_page()
        elif menu == "Reports/Prescription":
            self.reports_schedule()
        elif menu == "Expert Doctors Panel":
            self.hospitals_list()

    def register_patient(self):
        st.subheader("📝 New Patient Registration")
        with st.form("patient_registration"):
            self.app_id = random.randint(1, 9999)
            self.name = st.text_input("Patient Name")
            self.age = st.number_input("Age", min_value=0, max_value=120)
            self.sex = st.radio("Sex", ["M", "F"])
            self.state = st.text_input("State")
            self.city = st.text_input("City")
            self.address = st.text_area("Residential Address")
            self.password = st.text_input("Set Password", type="password")

            #csr1.execute("SELECT name, specialisation FROM doctorslist")
            #doctors = csr1.fetchall()
            #doctor_options = [f"{doc[0]} ({doc[1]})" for doc in doctors]
            #selected_doctor = st.selectbox("Choose Doctor", doctor_options)
            #self.doctor_appointed = selected_doctor.split(" (")[0]
            
            #problem = st.text_input("Suffering From")
            symptoms = st.text_area("Symptoms/Problem Facing")
            duration = st.text_input("Duration (e.g., 3 days, 2 weeks)")

            if st.form_submit_button("Register Patient"):
                csr2.execute(
                    'INSERT INTO patientlist VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (self.app_id, self.name, self.age, self.sex,
                     self.state, self.city, self.address, self.doctor_appointed, self.password, None, None, symptoms, duration, None, None)
                )
                sqldata2.commit()
                st.success(f"Registration Successful! Your Appointment ID: {self.app_id}")
                st.warning("Move to Login Page and Book Your Consultation")

    def login_page(self):
        st.subheader("🔑 Patient Login")
        appnum = st.number_input("Enter your Appointment ID", min_value=1)
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            csr2.execute("SELECT * FROM patientlist WHERE app_id = %s AND password = %s", (appnum, password))
            patient_data = csr2.fetchone()
    
            if patient_data:
                # Save to session_state
                st.session_state.logged_in = True
                st.session_state.app_id = patient_data[0]
                st.session_state.name = patient_data[1]
                st.session_state.age = patient_data[2]
                st.session_state.sex = patient_data[3]
                st.session_state.state = patient_data[4]
                st.session_state.city = patient_data[5]
                st.session_state.address = patient_data[6]
                st.session_state.doctor_appointed = patient_data[7]
    
                st.success("Login Successful!")
            else:
                st.session_state.logged_in = False
                st.error("Invalid Appointment ID or Password.")
    
        if st.session_state.get("logged_in"):
            self.book_consultation()

    def book_consultation(self):
        st.subheader("📅 Book Consultation")

        # Initialize edit mode session state
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False
    
        # Load additional medical info if not already in session
        if "symptom" not in st.session_state:
            csr2.execute("SELECT symptom, duration FROM patientlist WHERE app_id = %s", (st.session_state.app_id,))
            symptom_data = csr2.fetchone()
            if symptom_data:
                st.session_state.symptom = symptom_data[0]
                st.session_state.duration = symptom_data[1]
    
        # Show Patient Info
        st.write("🧾 Patient Details:")
        st.json({
            "Name": st.session_state.name,
            "Age": st.session_state.age,
            "Sex": st.session_state.sex,
            "State": st.session_state.state,
            "City": st.session_state.city,
            "Address": st.session_state.address,
            "Doctor_Appointed": st.session_state.get("doctor_appointed", "Not Selected"),
            "Symptoms": st.session_state.symptom,
            #"Suffering From": st.session_state.problem,
            "Duration": st.session_state.duration
        })
    
        # Toggle Edit Checkbox
        edit_toggle = st.checkbox("✏️ Edit Details", value=st.session_state.edit_mode)
    
        if edit_toggle:
            st.session_state.edit_mode = True
    
            with st.form("edit_form"):
                updated_name = st.text_input("Name", st.session_state.name)
                updated_age = st.number_input("Age", value=st.session_state.age, min_value=0, max_value=120)
                updated_sex = st.radio("Sex", ["M", "F"], index=0 if st.session_state.sex == "M" else 1)
                updated_state = st.text_input("State", st.session_state.state)
                updated_city = st.text_input("City", st.session_state.city)
                updated_address = st.text_area("Address", st.session_state.address)
    
                # New: Editable medical info
                updated_symptoms = st.text_area("Symptoms", st.session_state.get("symptoms", ""))
                updated_problem = st.text_input("Suffering From", st.session_state.get("problem", ""))
                updated_duration = st.text_input("Duration (e.g., 3 days, 2 weeks)", st.session_state.get("duration", ""))
    
                if st.form_submit_button("Save Changes"):
                    update_query = '''
                        UPDATE patientlist
                        SET name = %s, age = %s, sex = %s, state = %s,
                            city = %s, address = %s, symptoms = %s,
                            problem = %s, duration = %s
                        WHERE app_id = %s
                    '''
                    csr2.execute(update_query, (
                        updated_name, updated_age, updated_sex,
                        updated_state, updated_city, updated_address,
                        updated_symptoms, updated_problem, updated_duration,
                        st.session_state.app_id
                    ))
                    sqldata2.commit()
    
                    # Update session state
                    st.session_state.name = updated_name
                    st.session_state.age = updated_age
                    st.session_state.sex = updated_sex
                    st.session_state.state = updated_state
                    st.session_state.city = updated_city
                    st.session_state.address = updated_address
                    st.session_state.symptom = updated_symptom
                    #st.session_state.problem = updated_problem
                    st.session_state.duration = updated_duration
    
                    st.success("✅ Details updated successfully!")
                    st.session_state.edit_mode = False
                    st.rerun()
        else:
            st.session_state.edit_mode = False
    
        # --- Booking Section ---
        selected_date = st.date_input("Choose Consultation Date", key="date_picker")
        time_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"]
        selected_time = st.selectbox("Choose Time Slot", time_slots)
    
        # --- Choose Doctor Here ---
        csr1.execute("SELECT name, specialisation FROM doctorslist")
        doctors = csr1.fetchall()
        doctor_options = [f"{doc[0]} ({doc[1]})" for doc in doctors]
        selected_doctor = st.selectbox("Choose Doctor", doctor_options)
        chosen_doctor = selected_doctor.split(" (")[0]
    
        if st.button("Confirm Appointment"):
            csr2.execute(
                "SELECT COUNT(*) FROM patientlist WHERE app_date = %s AND app_time = %s",
                (selected_date, selected_time)
            )
            slot_count = csr2.fetchone()[0]
    
            if slot_count >= 5:
                st.error("😔 Slot full. Choose another time.")
            else:
                # Save date, time, and doctor
                csr2.execute(
                    '''UPDATE patientlist
                       SET app_date = %s, app_time = %s, doctor_appointed = %s
                       WHERE app_id = %s''',
                    (selected_date, selected_time, chosen_doctor, st.session_state.app_id)
                )
                sqldata2.commit()
    
                st.session_state.doctor_appointed = chosen_doctor
    
                st.success(
                    f"✅ Appointment confirmed with Dr. {chosen_doctor} on "
                    f"{selected_date.strftime('%d-%m-%Y')} at {selected_time}!"
                )
                
                st.info("Redirecting you to the Main Menu...")
                
                # Delay before rerun
                import time
                time.sleep(3)
                
                # Clear login state and redirect
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                st.experimental_rerun()


    def reports_schedule(self):
        st.subheader("📋 Reports & Prescription")
        st.info("Feature to be implemented.")

    def hospitals_list(self):
        st.subheader("🏨 Expert Doctors Panel")
        csr1.execute("SELECT * FROM doctorslist")
        for doc in csr1.fetchall():
            with st.expander(f"Dr. {doc[0]} ({doc[1]})"):
                st.write(f"Experience: {doc[5]} years")
                st.write(f"Past Hospitals: {doc[3]}")
                st.write(f"Contact: {doc[6]}")


if __name__ == "__main__":
    app = Appointment()
