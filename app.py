import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Payroll Reconciliation System",
    page_icon="💰",
    layout="wide"
)

st.title("Payroll Reconciliation System")

st.write(
    "An application for reconciling employee payroll "
    "against actual bank payments."
)

st.divider()


def get_connection():

    connection = sqlite3.connect("payroll.db")

    return connection


def get_record_counts():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM payroll")
    total_payroll = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bank_transactions")
    total_transactions = cursor.fetchone()[0]

    connection.close()

    return total_employees, total_payroll, total_transactions



st.subheader("Database Overview")

total_employees, total_payroll, total_transactions = get_record_counts()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Employees", total_employees)

with col2:
    st.metric("Payroll Records", total_payroll)

with col3:
    st.metric("Bank Transactions", total_transactions)




def get_reconciliation_data():

    connection = get_connection()

    query = """
        SELECT
            e.employee_id,
            e.employee_name,
            e.department,
            p.payroll_period,
            p.net_pay,
            b.amount_paid

        FROM employees e

        LEFT JOIN payroll p
            ON e.employee_id = p.employee_id

        LEFT JOIN (
            SELECT
                employee_id,
                SUBSTR(transaction_date, 1, 7) AS payroll_period,
                SUM(amount_paid) AS amount_paid
            FROM bank_transactions
            GROUP BY
                employee_id,
                SUBSTR(transaction_date, 1, 7)
        ) b
            ON e.employee_id = b.employee_id
            AND p.payroll_period = b.payroll_period

        WHERE e.employment_status = 'Active'
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


def calculate_reconciliation(df):

    statuses = []
    variances = []

    for index, row in df.iterrows():

        expected_pay = row["net_pay"]
        actual_pay = row["amount_paid"]

        if pd.isna(expected_pay):
            status = "No Payroll Record"
            variance = None

        elif pd.isna(actual_pay):
            status = "Not Paid"
            variance = expected_pay

        else:
            variance = round(float(expected_pay) - float(actual_pay), 2)

            if variance == 0:
                status = "Fully Paid"

            elif variance > 0:
                status = "Underpaid"

            else:
                status = "Overpaid"

        statuses.append(status)
        variances.append(variance)

    df["Variance"] = variances
    df["Payment Status"] = statuses

    return df


st.divider()

st.header("Payroll Reconciliation Results")

reconciliation_df = get_reconciliation_data()

reconciliation_df = calculate_reconciliation(reconciliation_df)

fully_paid = len(reconciliation_df[
    reconciliation_df["Payment Status"] == "Fully Paid"
])

underpaid = len(reconciliation_df[
    reconciliation_df["Payment Status"] == "Underpaid"
])

overpaid = len(reconciliation_df[
    reconciliation_df["Payment Status"] == "Overpaid"
])

not_paid = len(reconciliation_df[
    reconciliation_df["Payment Status"] == "Not Paid"
])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Fully Paid", fully_paid)

col2.metric("Underpaid", underpaid)

col3.metric("Overpaid", overpaid)

col4.metric("Not Paid", not_paid)



st.subheader("Payment Status Overview")

payment_summary = pd.DataFrame({
    "Payment Status": [
        "Fully Paid",
        "Underpaid",
        "Overpaid",
        "Not Paid"
    ],

    "Number of Employees": [
        fully_paid,
        underpaid,
        overpaid,
        not_paid
    ]
})

payment_summary = payment_summary.set_index("Payment Status")

st.bar_chart(payment_summary)


total_reconciled = fully_paid + underpaid + overpaid + not_paid

payment_summary["Percentage"] = (
    payment_summary["Number of Employees"]
    / total_reconciled * 100
)

st.subheader("Payment Status Percentages")

st.dataframe(payment_summary)


st.divider()

st.header("Payroll Financial Summary")

total_expected_payroll = (
    reconciliation_df["net_pay"].fillna(0).sum()
)

total_actual_paid = (
    reconciliation_df["amount_paid"].fillna(0).sum()
)

total_underpayment = (
    reconciliation_df["Variance"]
    .clip(lower=0)
    .sum()
)

total_overpayment = (
    -reconciliation_df["Variance"]
    .clip(upper=0)
    .sum()
)



st.subheader("Detailed Reconciliation Report")

st.dataframe(reconciliation_df, use_container_width=True)





st.divider()

st.subheader("Payroll Exceptions Report")

exceptions_df = reconciliation_df[
    reconciliation_df["Payment Status"].isin([
        "Underpaid",
        "Overpaid",
        "Not Paid",
        "No Payroll Record"
    ])
]

st.metric("Total Payroll Exceptions", len(exceptions_df))

if len(exceptions_df) > 0:

    st.warning("Some payroll records require investigation.")

    st.dataframe(
        exceptions_df,
        use_container_width=True
    )

else:

    st.success("No payroll exceptions identified.")



excel_buffer = BytesIO()

with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:

    exceptions_df.to_excel(
        writer,
        index=False,
        sheet_name="Payroll Exceptions"
    )

excel_buffer.seek(0)

st.download_button(
    label="Download Payroll Exceptions Report",
    data=excel_buffer,
    file_name="payroll_exceptions.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)




col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Expected Net Payroll",
    f"KES {total_expected_payroll:,.2f}"
)

col2.metric(
    "Actual Amount Paid",
    f"KES {total_actual_paid:,.2f}"
)

col3.metric(
    "Total Underpayment",
    f"KES {total_underpayment:,.2f}"
)

col4.metric(
    "Total Overpayment",
    f"KES {total_overpayment:,.2f}"
)



st.subheader("Expected vs Actual Payroll")

payroll_comparison = pd.DataFrame({
    "Payroll Category": [
        "Expected Payroll",
        "Actual Payments"
    ],

    "Amount (KES)": [
        total_expected_payroll,
        total_actual_paid
    ]
})

payroll_comparison = payroll_comparison.set_index(
    "Payroll Category"
)

st.bar_chart(payroll_comparison)


def get_unmatched_transactions():

    connection = get_connection()

    query = """
        SELECT
            b.transaction_id,
            b.transaction_date,
            b.employee_id,
            b.amount_paid,
            b.reference

        FROM bank_transactions b

        LEFT JOIN employees e
            ON b.employee_id = e.employee_id

        WHERE e.employee_id IS NULL
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


st.divider()

st.header("Unmatched Bank Transactions")

unmatched_df = get_unmatched_transactions()

st.metric("Unmatched Transactions", len(unmatched_df))

if len(unmatched_df) > 0:

    st.warning("Some bank transactions could not be matched to employees.")

    st.dataframe(unmatched_df, use_container_width=True)

else:

    st.success("All bank transactions have been matched to employees.")



def get_employees():

    connection = get_connection()

    query = "SELECT * FROM employees"

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


st.divider()

st.header("Employee Management")

employees_df = get_employees()

st.dataframe(employees_df, use_container_width=True)




st.subheader("Register New Employee")

with st.form("add_employee_form"):

    employee_id = st.text_input("Employee ID")

    employee_name = st.text_input("Employee Name")

    department = st.text_input("Department")

    job_grade = st.text_input("Job Grade")

    employment_status = st.selectbox(
        "Employment Status",
        ["Active", "Inactive"]
    )

    submitted = st.form_submit_button("Add Employee")

    if submitted:

        if not employee_id or not employee_name:
            st.error("Employee ID and Name are required.")

        else:

            connection = get_connection()

            try:

                cursor = connection.cursor()

                cursor.execute("""
                    INSERT INTO employees
                    (employee_id, employee_name, department,
                     job_grade, employment_status)

                    VALUES (?, ?, ?, ?, ?)
                """, (
                    employee_id,
                    employee_name,
                    department,
                    job_grade,
                    employment_status
                ))

                connection.commit()

                st.success("Employee added successfully!")

                st.rerun()

            except sqlite3.IntegrityError:

                st.error("This Employee ID already exists.")

            finally:

                connection.close()





st.subheader("Delete Employee")

employee_to_delete = st.text_input("Enter Employee ID to delete")

if st.button("Delete Employee"):
    if not employee_to_delete:
        st.error("Please enter an Employee ID.")
    else:
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM employees WHERE employee_id = ?",
                (employee_to_delete,)
            )

            connection.commit()

            if cursor.rowcount > 0:
                st.success("Employee deleted successfully!")
                st.rerun()
            else:
                st.warning("Employee ID not found.")

        except sqlite3.Error as error:
            st.error(f"Database error: {error}")

        finally:
            connection.close()




st.subheader("Update Employee")

with st.form("update_employee_form"):

    update_id = st.text_input("Employee ID to update")
    new_department = st.text_input("New Department")
    new_job_grade = st.text_input("New Job Grade")

    new_status = st.selectbox(
        "New Employment Status",
        ["Active", "Inactive"]
    )

    update_submitted = st.form_submit_button("Update Employee")

    if update_submitted:

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE employees
                SET department = ?,
                    job_grade = ?,
                    employment_status = ?
                WHERE employee_id = ?
            """, (
                new_department,
                new_job_grade,
                new_status,
                update_id
            ))

            connection.commit()

            if cursor.rowcount > 0:
                st.success("Employee updated successfully!")
                st.rerun()
            else:
                st.warning("Employee ID not found.")

        except sqlite3.Error as error:
            st.error(f"Database error: {error}")

        finally:
            connection.close()