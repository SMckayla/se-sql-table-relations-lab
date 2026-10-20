# STEP 0

# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1
# Employees working in the Boston office.
df_boston = pd.read_sql("""
SELECT
    employees.firstName,
    employees.lastName
FROM employees
JOIN offices
    ON employees.officeCode = offices.officeCode
WHERE offices.city = 'Boston'
ORDER BY employees.firstName
""", conn)

# STEP 2
# Offices that have no employees. Every office is staffed, so this is empty.
df_zero_emp = pd.read_sql("""
SELECT
    offices.officeCode,
    offices.city
FROM offices
LEFT JOIN employees
    ON offices.officeCode = employees.officeCode
GROUP BY offices.officeCode, offices.city
HAVING COUNT(employees.employeeNumber) = 0
""", conn)

# STEP 3
# Every employee, with the city and state of their office.
df_employee = pd.read_sql("""
SELECT
    employees.firstName,
    employees.lastName,
    offices.city,
    offices.state
FROM employees
LEFT JOIN offices
    ON employees.officeCode = offices.officeCode
ORDER BY employees.firstName, employees.lastName
""", conn)

# STEP 4
# Customers who have never placed an order.
df_contacts = pd.read_sql("""
SELECT
    customers.contactFirstName,
    customers.contactLastName,
    customers.phone,
    customers.salesRepEmployeeNumber
FROM customers
LEFT JOIN orders
    ON customers.customerNumber = orders.customerNumber
WHERE orders.orderNumber IS NULL
ORDER BY customers.contactLastName
""", conn)

# STEP 5
# amount is stored as text, so cast it before sorting numerically.
df_payment = pd.read_sql("""
SELECT
    customers.contactFirstName,
    customers.contactLastName,
    CAST(payments.amount AS REAL) AS amount,
    payments.paymentDate
FROM customers
JOIN payments
    ON customers.customerNumber = payments.customerNumber
ORDER BY amount DESC
""", conn)

# STEP 6
# Sales reps whose customers have an average credit limit over 90,000.
df_credit = pd.read_sql("""
SELECT
    employees.employeeNumber,
    employees.firstName,
    employees.lastName,
    COUNT(customers.customerNumber) AS n_customers
FROM employees
JOIN customers
    ON employees.employeeNumber = customers.salesRepEmployeeNumber
GROUP BY
    employees.employeeNumber,
    employees.firstName,
    employees.lastName
HAVING AVG(customers.creditLimit) > 90000
ORDER BY n_customers DESC
""", conn)

# STEP 7
# How many times each product was ordered, and how many units sold.
df_product_sold = pd.read_sql("""
SELECT
    products.productName,
    COUNT(orderdetails.orderNumber) AS numorders,
    SUM(orderdetails.quantityOrdered) AS totalunits
FROM products
JOIN orderdetails
    ON products.productCode = orderdetails.productCode
GROUP BY products.productCode, products.productName
ORDER BY totalunits DESC
""", conn)

# STEP 8
# How many different customers have ordered each product.
df_total_customers = pd.read_sql("""
SELECT
    products.productName,
    products.productCode,
    COUNT(DISTINCT orders.customerNumber) AS numpurchasers
FROM products
JOIN orderdetails
    ON products.productCode = orderdetails.productCode
JOIN orders
    ON orderdetails.orderNumber = orders.orderNumber
GROUP BY products.productCode, products.productName
ORDER BY numpurchasers DESC
""", conn)

# STEP 9
# Customers assigned to each office through their sales rep.
df_customers = pd.read_sql("""
SELECT
    offices.officeCode,
    offices.city,
    COUNT(customers.customerNumber) AS n_customers
FROM offices
JOIN employees
    ON offices.officeCode = employees.officeCode
JOIN customers
    ON employees.employeeNumber = customers.salesRepEmployeeNumber
GROUP BY offices.officeCode, offices.city
ORDER BY offices.officeCode
""", conn)

# STEP 10
# Employees who sold a product ordered by fewer than 20 customers.
df_under_20 = pd.read_sql("""
SELECT DISTINCT
    employees.employeeNumber,
    employees.firstName,
    employees.lastName,
    offices.city,
    offices.officeCode
FROM employees
JOIN offices
    ON employees.officeCode = offices.officeCode
JOIN customers
    ON employees.employeeNumber = customers.salesRepEmployeeNumber
JOIN orders
    ON customers.customerNumber = orders.customerNumber
JOIN orderdetails
    ON orders.orderNumber = orderdetails.orderNumber
WHERE orderdetails.productCode IN (
    SELECT productCode
    FROM orderdetails
    JOIN orders
        USING(orderNumber)
    GROUP BY productCode
    HAVING COUNT(DISTINCT customerNumber) < 20
)
ORDER BY employees.lastName, employees.firstName
""", conn)

conn.close()
