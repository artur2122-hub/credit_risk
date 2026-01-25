CREATE OR REPLACE VIEW v_features AS
WITH base AS (
  SELECT
    CAST(default_next_month AS INTEGER) AS default_next_month,

    CAST(limit_bal AS DOUBLE) AS limit_bal,
    CAST(age AS INTEGER)      AS age,

    CAST(sex AS INTEGER)       AS sex,
    CAST(education AS INTEGER) AS education,
    CAST(marriage AS INTEGER)  AS marriage,

    CAST(pay_0 AS INTEGER) AS pay_0,
    CAST(pay_2 AS INTEGER) AS pay_2,
    CAST(pay_3 AS INTEGER) AS pay_3,
    CAST(pay_4 AS INTEGER) AS pay_4,
    CAST(pay_5 AS INTEGER) AS pay_5,
    CAST(pay_6 AS INTEGER) AS pay_6,

    CAST(bill_amt1 AS DOUBLE) AS bill_amt1,
    CAST(bill_amt2 AS DOUBLE) AS bill_amt2,
    CAST(bill_amt3 AS DOUBLE) AS bill_amt3,

    CAST(pay_amt1 AS DOUBLE)  AS pay_amt1,
    CAST(pay_amt2 AS DOUBLE)  AS pay_amt2,
    CAST(pay_amt3 AS DOUBLE)  AS pay_amt3
  FROM v_clients
),
ratios AS (
  SELECT
    *,
    CASE WHEN pay_0 >= 1 THEN 1 ELSE 0 END AS any_delay,
    CASE WHEN pay_0 >= 2 THEN 1 ELSE 0 END AS serious_delay,

    bill_amt1 / NULLIF(limit_bal, 0) AS utilization_ratio,
    pay_amt1  / NULLIF(bill_amt1, 0) AS payment_ratio,

    (bill_amt1 + bill_amt2 + bill_amt3) / 3.0 AS avg_bill_3m,
    (pay_amt1  + pay_amt2  + pay_amt3 ) / 3.0 AS avg_pay_3m,

    ((bill_amt1 + bill_amt2 + bill_amt3) - (pay_amt1 + pay_amt2 + pay_amt3)) AS net_bill_minus_pay_3m
  FROM base
)
SELECT
  default_next_month,
  limit_bal,
  age,
  sex, education, marriage,

  pay_0,
  any_delay,
  serious_delay,

  utilization_ratio,
  payment_ratio,
  CASE WHEN payment_ratio IS NULL THEN 1 ELSE 0 END AS payment_ratio_missing,

  avg_bill_3m,
  avg_pay_3m,
  net_bill_minus_pay_3m,

  (
    (CASE WHEN pay_0 >= 1 THEN 1 ELSE 0 END) +
    (CASE WHEN pay_2 >= 1 THEN 1 ELSE 0 END) +
    (CASE WHEN pay_3 >= 1 THEN 1 ELSE 0 END) +
    (CASE WHEN pay_4 >= 1 THEN 1 ELSE 0 END) +
    (CASE WHEN pay_5 >= 1 THEN 1 ELSE 0 END) +
    (CASE WHEN pay_6 >= 1 THEN 1 ELSE 0 END)
  ) AS n_months_late_6m,

  -- optional improvement (see below)
  GREATEST(0,pay_0, pay_2, pay_3, pay_4, pay_5, pay_6) AS max_late_6m
FROM ratios;

