# pylint:disable=C0111,C0103
import sqlite3

conn = sqlite3.connect('data/ecommerce.sqlite')

def get_average_purchase(db):
    # return the average amount spent per order for each customer ordered by customer ID
    query = '''
    SELECT DISTINCT
	Orders.CustomerID,
	ROUND(SUM(OrderDetails.UnitPrice*OrderDetails.Quantity)/COUNT(DISTINCT Orders.OrderID),2) AS amount
    FROM Orders
    JOIN OrderDetails ON OrderDetails.OrderID = Orders.OrderID
    GROUP BY Orders.CustomerID
    ORDER BY Orders.CustomerID
    '''
    db.execute(query)
    results = db.fetchall()
    return results

def get_general_avg_order(db):
    # return the average amount spent per order
    query = '''
    SELECT
	ROUND(SUM(OrderDetails.UnitPrice*OrderDetails.Quantity)/
    COUNT(DISTINCT OrderDetails.OrderID)) AS GeneralAverageOrderAmount
    FROM OrderDetails
    '''
    db.execute(query)
    results = db.fetchone()
    return float(results[0])

def best_customers(db):
    # return the customers who have an average purchase greater than the general average purchase
    query = '''
    WITH best AS (
	SELECT DISTINCT
		Orders.CustomerID AS ID,
		ROUND(SUM(OrderDetails.UnitPrice*OrderDetails.Quantity)/COUNT(DISTINCT Orders.OrderID),2) AS c_amount,
		(SELECT
			ROUND(SUM(OrderDetails.UnitPrice*OrderDetails.Quantity)/
    		COUNT(DISTINCT OrderDetails.OrderID)) AS GeneralAverageOrderAmount
    	FROM OrderDetails) AS general_amount
	FROM Orders
	JOIN OrderDetails ON OrderDetails.OrderID = Orders.OrderID
	GROUP BY Orders.CustomerID
    ORDER BY c_amount DESC
)
SELECT
	best.ID AS CustomerID,
	best.c_amount AS OrderedAmount
FROM best
WHERE best.c_amount >= best.general_amount
    '''
    db.execute(query)
    results = db.fetchall()
    return results

def top_ordered_product_per_customer(db):
    # return the list of the top ordered product by each customer
    # based on the total ordered amount in USD
    query = '''
     WITH products AS (
        SELECT
	    Orders.CustomerID AS CustomerID,
	    OrderDetails.ProductID AS ProductID,
	    SUM(OrderDetails.UnitPrice*OrderDetails.Quantity)AS Amount
    FROM OrderDetails
    JOIN Orders ON OrderDetails.OrderID = Orders.OrderID
    GROUP BY CustomerID, ProductID
    ORDER BY Amount DESC
    )
    SELECT
	    products.CustomerID AS Customer_ID,
	    products.ProductID AS Product_ID,
	    products.Amount AS OrderedAmount
    FROM products
    GROUP BY Customer_ID
    ORDER BY OrderedAmount DESC
    '''
    db.execute(query)
    results = db.fetchall()
    return results

def average_number_of_days_between_orders(db):
    # return the average number of days between two consecutive orders of the same customer
    query = '''
        SELECT
	    CAST(ROUND(AVG(DaysBetweenOrders)) AS INTEGER)
	    FROM (SELECT
	    CustomerID,
	    OrderDate,
	    JULIANDAY(OrderDate) - JULIANDAY(LAG(OrderDate) OVER (
	    PARTITION BY CustomerID
        ORDER BY OrderDate
        ))AS DaysBetweenOrders
        FROM Orders)
    '''
    db.execute(query)
    results = db.fetchone()
    return results[0]
