SELECT
    item_name,
    COUNT(transaction_id) transaction_count
FROM orders
GROUP BY item_name
ORDER BY COUNT(transaction_id) DESC
LIMIT 3;