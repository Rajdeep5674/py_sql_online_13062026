import os
import streamlit as st
import mysql.connector
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Database Connection Function
# -----------------------------
def get_connection():
    conn_obj = mysql.connector.connect(
        host="thomas.proxy.rlwy.net",
        port=53904,
        user="root",
        password="HAMJgeZYUwShZliUAlpWTmIBHnVBaJIC",
        database="railway"
    )
    return conn_obj


# -----------------------------
# Fetch Table Structure
# -----------------------------
def get_table_columns():
    conn_obj = get_connection()
    cur_obj = conn_obj.cursor(dictionary=True)

    cur_obj.execute("DESCRIBE railway.emp_table")
    columns = cur_obj.fetchall()

    cur_obj.close()
    conn_obj.close()

    return columns


# -----------------------------
# Insert Data Function
# -----------------------------
def insert_data(data_dict):
    conn_obj = get_connection()
    cur_obj = conn_obj.cursor()

    columns = list(data_dict.keys())
    values = list(data_dict.values())

    column_names = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(values))

    query = f"""
    INSERT INTO railway.emp_table ({column_names})
    VALUES ({placeholders})
    """

    cur_obj.execute(query, values)
    conn_obj.commit()

    cur_obj.close()
    conn_obj.close()


# -----------------------------
# Fetch Data Function
# -----------------------------
def fetch_data():
    conn_obj = get_connection()

    query = "SELECT * FROM railway.emp_table"
    df = pd.read_sql(query, conn_obj)

    conn_obj.close()

    return df


# -----------------------------
# Streamlit Frontend
# -----------------------------
st.set_page_config(page_title="Cloud MySQL Insert App", layout="wide")

st.title("Employee Data Entry App")
st.write("Insert records into Railway MySQL cloud table: `railway.emp_table`")

menu = st.sidebar.radio(
    "Select Option",
    ["Insert Data", "View Data"]
)

if menu == "Insert Data":

    st.subheader("Insert New Employee Record")

    try:
        columns = get_table_columns()

        data_dict = {}

        with st.form("insert_form"):

            for col in columns:
                column_name = col["Field"]
                data_type = col["Type"]
                extra = col["Extra"]
                is_nullable = col["Null"]

                # Skip AUTO_INCREMENT column
                if "auto_increment" in extra.lower():
                    continue

                # Create input fields based on datatype
                if "int" in data_type:
                    value = st.number_input(
                        f"{column_name} ({data_type})",
                        step=1,
                        format="%d"
                    )

                elif "decimal" in data_type or "float" in data_type or "double" in data_type:
                    value = st.number_input(
                        f"{column_name} ({data_type})",
                        step=0.01
                    )

                elif "date" in data_type:
                    value = st.date_input(
                        f"{column_name} ({data_type})"
                    )

                elif "datetime" in data_type or "timestamp" in data_type:
                    value = st.text_input(
                        f"{column_name} ({data_type})",
                        placeholder="YYYY-MM-DD HH:MM:SS"
                    )

                else:
                    value = st.text_input(
                        f"{column_name} ({data_type})"
                    )

                data_dict[column_name] = value

            submit_btn = st.form_submit_button("Insert Record")

        if submit_btn:
            insert_data(data_dict)
            st.success("Record inserted successfully into cloud MySQL table.")

    except mysql.connector.Error as e:
        st.error("Database error occurred.")
        st.write(e)

    except Exception as e:
        st.error("Something went wrong.")
        st.write(e)


elif menu == "View Data":

    st.subheader("Employee Table Records")

    try:
        df = fetch_data()
        st.dataframe(df, use_container_width=True)

    except mysql.connector.Error as e:
        st.error("Database error occurred.")
        st.write(e)

    except Exception as e:
        st.error("Something went wrong.")
        st.write(e)