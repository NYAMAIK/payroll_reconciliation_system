import sqlite3
import csv

def create_database():

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            employee_name TEXT,
            department TEXT,
            job_grade TEXT,
            employment_status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_period TEXT,
            employee_id TEXT,
            net_pay REAL,
            UNIQUE(payroll_period, employee_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank_transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date TEXT,
            employee_id TEXT,
            amount_paid REAL,
            reference TEXT
        )
    """)

    connection.commit()

    connection.close()

def insert_employees():

    connection = None

    try:
        connection = sqlite3.connect("payroll.db")
        cursor = connection.cursor()

        with open("data/employees.csv", mode="r", newline="", encoding="utf-8") as file:

            employee_reader = csv.DictReader(file)

            for employee in employee_reader:

                cursor.execute("""
                    INSERT OR IGNORE INTO employees
                    (employee_id, employee_name, department, job_grade, employment_status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    employee["employee_id"],
                    employee["employee_name"],
                    employee["department"],
                    employee["job_grade"],
                    employee["employment_status"]
                ))

        connection.commit()

        print("Employee records inserted successfully!")

    except FileNotFoundError:
        if connection:
            connection.rollback()

        print("Error: The employees.csv file could not be found.")

    except KeyError as error:
        if connection:
            connection.rollback()
                  
        print(f"CSV file error: Missing column {error}")

    except sqlite3.Error as error:
        if connection:
            connection.rollback()
                  
        print("Database error:", error)

    except Exception as error:
        if connection:
            connection.rollback()
                  
        print("An unexpected error occurred:", error)

    finally:
        if connection:
            connection.close()

def count_employees():

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")

    total = cursor.fetchone()[0]

    print("Total employees in database:", total)

    connection.close()



def insert_payroll():

    connection = None

    try:
        connection = sqlite3.connect("payroll.db")
        cursor = connection.cursor()

        inserted_count = 0
        duplicate_count = 0

        with open("data/payroll.csv", mode="r", newline="", encoding="utf-8") as file:

            payroll_reader = csv.DictReader(file)

            required_columns = [
                "payroll_period",
                "employee_id",
                "net_pay"
            ]

            missing_columns = set(required_columns) - set(payroll_reader.fieldnames or [])

            if missing_columns:
                raise ValueError(f"Missing CSV columns: {missing_columns}")

            for payroll in payroll_reader:

                cursor.execute("""
                    INSERT OR IGNORE INTO payroll
                    (payroll_period, employee_id, net_pay)
                    VALUES (?, ?, ?)
                """, (
                    payroll["payroll_period"],
                    payroll["employee_id"],
                    payroll["net_pay"]
                ))

                if cursor.rowcount > 0:
                    inserted_count += 1
                else:
                    duplicate_count += 1

        connection.commit()

        print(f"Payroll records inserted: {inserted_count}")
        print(f"Duplicate payroll records ignored: {duplicate_count}")

    except FileNotFoundError:
        if connection:
            connection.rollback()

        print("Error: The payroll.csv file could not be found.")

    except KeyError as error:
        if connection:
            connection.rollback()

        print(f"CSV file error: Missing column {error}")

    except ValueError as error:
        if connection:
            connection.rollback()

        print(f"CSV validation error: {error}")

    except sqlite3.Error as error:
        if connection:
            connection.rollback()

        print(f"Database error: {error}")

    except Exception as error:
        if connection:
            connection.rollback()

        print(f"An unexpected error occurred: {error}")

    finally:
        if connection:
            connection.close()


def view_payroll():

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM payroll")

    payroll_records = cursor.fetchall()

    for payroll in payroll_records:
        print(payroll)

    connection.close()

def count_payroll():

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM payroll")

    total = cursor.fetchone()[0]

    print("Total payroll records:", total)

    connection.close()

def count_bank_transactions():

    connection = sqlite3.connect("payroll.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM bank_transactions")

    total = cursor.fetchone()[0]

    print("Total bank transactions:", total)

    connection.close()




def insert_bank_transactions():

    connection = None

    try:
        connection = sqlite3.connect("payroll.db")
        cursor = connection.cursor()

        inserted_count = 0
        duplicate_count = 0

        with open("data/bank_statement.csv", mode="r", newline="", encoding="utf-8") as file:

            bank_reader = csv.DictReader(file)

            required_columns = [
                "transaction_id",
                "transaction_date",
                "employee_id",
                "amount_paid",
                "reference"
            ]

            missing_columns = set(required_columns) - set(bank_reader.fieldnames or [])

            if missing_columns:
                raise ValueError(f"Missing CSV columns: {missing_columns}")

            for transaction in bank_reader:

                cursor.execute("""
                    INSERT OR IGNORE INTO bank_transactions
                    (transaction_id, transaction_date, employee_id, amount_paid, reference)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    transaction["transaction_id"],
                    transaction["transaction_date"],
                    transaction["employee_id"],
                    transaction["amount_paid"],
                    transaction["reference"]
                ))

                if cursor.rowcount > 0:
                    inserted_count += 1
                else:
                    duplicate_count += 1

        connection.commit()

        print(f"Bank transactions inserted: {inserted_count}")
        print(f"Duplicate transactions ignored: {duplicate_count}")

    except FileNotFoundError:
        if connection:
            connection.rollback()

        print("Error: Bank statement CSV file was not found.")

    except KeyError as error:
        if connection:
            connection.rollback()

        print(f"CSV file error: Missing column {error}")

    except ValueError as error:
        if connection:
            connection.rollback()

        print(f"CSV validation error: {error}")

    except sqlite3.Error as error:
        if connection:
            connection.rollback()

        print(f"Database error: {error}")

    except Exception as error:
        if connection:
            connection.rollback()

        print(f"An unexpected error occurred: {error}")

    finally:
        if connection:
            connection.close()




if __name__ == "__main__":

    create_database()

    insert_employees()
    insert_payroll()
    insert_bank_transactions()

    count_employees()
    count_payroll()
    count_bank_transactions()
