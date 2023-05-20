SELECT 
    membership_id,
    SUM(total_price) AS total_spending
FROM transactions
GROUP BY membership_id
ORDER BY total_spending DESC
LIMIT 10;