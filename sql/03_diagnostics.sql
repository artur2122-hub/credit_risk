SELECT 
	default_next_month,
	COUNT(*) AS n
FROM v_clients
GROUP BY default_next_month;

SELECT
	default_next_month,
	COUNT(*) AS n,
	ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM v_clients
GROUP BY default_next_month
ORDER BY default_next_month;
	
SELECT COUNT(*) AS n_raw FROM raw_default_clients;
SELECT COUNT(*) AS n_clients FROM v_clients;
SELECT COUNT(*) AS n_features FROM v_features;


SELECT 
	default_next_month,
	COUNT(*) AS n,
	ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct
FROM v_clients
GROUP BY default_next_month
ORDER BY default_next_month;


SELECT 
	default_next_month,
	COUNT(*) AS n, 
	AVG(pay_0) AS avg_pay_0,
	AVG(utilization_ratio) AS avg_util,
	AVG(payment_ratio) AS avg_pay_ratio
FROM v_features
GROUP BY default_next_month
ORDER BY default_next_month;


DESCRIBE v_features;

SELECT
	default_next_month,
	AVG(n_months_late_6m) AS avg_late_months,
	AVG(max_late_6m) AS avg_max_late,
	AVG(payment_ratio_missing) AS pct_missing_pay_ratio
FROM v_features
GROUP BY default_next_month 
ORDER BY default_next_month;

