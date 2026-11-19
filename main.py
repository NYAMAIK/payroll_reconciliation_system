import sqlite3

class Employee:

    def __init__(self, employee_id, employee_name, department, job_grade, employment_status):

        self.employee_id = employee_id
        self.employee_name = employee_name
        self.department = department
        self.job_grade = job_grade
        self.employment_status = employment_status

    def display_details(self):

        print("Employee ID:", self.employee_id)
        print("Employee Name:", self.employee_name)
        print("Department:", self.department)
        print("Job Grade:", self.job_grade)
        print("Employment Status:", self.employment_status)

    def is_active(self):

        return self.employment_status == "Active"
    
class Payroll:
    def __init__(self, payroll_period, employee_id, net_pay):
        self.payroll_period = payroll_period
        self.employee_id = employee_id
        self.net_pay = net_pay

    def calculate_variance(self, actual_pay):
        expected_pay = int(self.net_pay)
        actual_pay = int(actual_pay)

        variance = expected_pay - actual_pay

        return variance

class BankTransaction:

    def __init__(self, transaction_id, transaction_date, employee_id, amount_paid, reference):

        self.transaction_id = transaction_id
        self.transaction_date = transaction_date
        self.employee_id = employee_id
        self.amount_paid = amount_paid
        self.reference = reference

    def is_valid_payment(self):
        return int(self.amount_paid) > 0


def load_employees():

    employees = []

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM employees")

    employee_records = cursor.fetchall()

    for employee in employee_records:

        employee_object = Employee(
            employee[0],
            employee[1],
            employee[2],
            employee[3],
            employee[4]
        )

        employees.append(employee_object)

    connection.close()

    return employees


def load_payroll():

    payroll_records = []

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM payroll")

    records = cursor.fetchall()

    for payroll in records:

        payroll_object = Payroll(
            payroll[1],
            payroll[2],
            payroll[3]
        )

        payroll_records.append(payroll_object)

    connection.close()

    return payroll_records



def load_bank_transactions():

    bank_transactions = []

    connection = sqlite3.connect("payroll.db")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bank_transactions")

    records = cursor.fetchall()

    for transaction in records:

        transaction_object = BankTransaction(
            transaction[0],
            transaction[1],
            transaction[2],
            transaction[3],
            transaction[4]
        )

        bank_transactions.append(transaction_object)

    connection.close()

    return bank_transactions


def reconcile_payroll(employees, payroll_records, bank_transactions):

    print("EMPLOYEE RECORDS:", len(employees))
    print("PAYROLL RECORDS:", len(payroll_records))
    print("BANK TRANSACTIONS:", len(bank_transactions))

    print("\n========== PAYROLL RECONCILIATION REPORT ==========")

    fully_paid_count = 0
    underpaid_count = 0
    overpaid_count = 0
    not_paid_count = 0
    unmatched_transactions_count = 0

    for employee in employees:

        if not employee.is_active():
            print(employee.employee_name, "is inactive - skipping reconciliation")
            continue

        for payroll in payroll_records:

            if employee.employee_id == payroll.employee_id:

                payment_found = False

                for transaction in bank_transactions:

                    if employee.employee_id == transaction.employee_id:

                        payment_found = True

                        expected_pay = int(payroll.net_pay)
                        actual_pay = int(transaction.amount_paid)

                        variance = payroll.calculate_variance(transaction.amount_paid)

                        print(f"\nEmployee: {employee.employee_name}")
                        print(f"Expected Pay: KES. {expected_pay:,}")
                        print(f"Actual Pay: KES. {actual_pay:,}")
                        print(f"Variance: KES. {variance:,}")

                        if variance == 0:
                            status = "Fully paid"
                            fully_paid_count += 1

                        elif variance > 0:
                            status = "Underpayment"
                            underpaid_count += 1

                        else:
                            status = "Overpayment"
                            overpaid_count += 1

                        print(f"Payment Status: {status}")

                if payment_found == False:
                    not_paid_count += 1
                    print(f"{employee.employee_name}: Not Paid")

    for transaction in bank_transactions:

        employee_found = False

        for employee in employees:

            if transaction.employee_id == employee.employee_id:
                employee_found = True

        if employee_found == False:
            unmatched_transactions_count += 1
            print(f"Unmatched transaction: {transaction.employee_id}")

    print("\n========== RECONCILIATION SUMMARY ==========")

    print(f"Fully Paid: {fully_paid_count}")
    print(f"Underpaid: {underpaid_count}")
    print(f"Overpaid: {overpaid_count}")
    print(f"Not Paid: {not_paid_count}")
    print(f"Unmatched Transactions: {unmatched_transactions_count}")

if __name__ == "__main__":

    employees = load_employees()

    payroll_records = load_payroll()

    bank_transactions = load_bank_transactions()

    reconcile_payroll(employees, payroll_records, bank_transactions)