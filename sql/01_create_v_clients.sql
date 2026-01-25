CREATE OR REPLACE TABLE raw_default_clients AS
SELECT *
FROM read_parquet('/data/ds/projects/credit-risk-prediction/data/processed/default_clients.parquet');

SELECT COUNT(*) FROM raw_default_clients;

CREATE OR REPLACE VIEW v_clients AS
SELECT
  X1  AS limit_bal,
  X2  AS sex,
  X3  AS education,
  X4  AS marriage,
  X5  AS age,

  X6  AS pay_0,
  X7  AS pay_2,
  X8  AS pay_3,
  X9  AS pay_4,
  X10 AS pay_5,
  X11 AS pay_6,

  X12 AS bill_amt1,
  X13 AS bill_amt2,
  X14 AS bill_amt3,
  X15 AS bill_amt4,
  X16 AS bill_amt5,
  X17 AS bill_amt6,

  X18 AS pay_amt1,
  X19 AS pay_amt2,
  X20 AS pay_amt3,
  X21 AS pay_amt4,
  X22 AS pay_amt5,
  X23 AS pay_amt6,

  Y   AS default_next_month
FROM raw_default_clients
WHERE CAST(X1 AS VARCHAR) <> 'LIMIT_BAL';

	