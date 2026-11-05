create database stockwise;

use stockwise;

CREATE OR REPLACE VIEW sales_analysis AS
SELECT
    STR_TO_DATE(`Date`, '%Y-%m-%d') AS sales_date,
    `Store ID`,
    `Product ID`,
    `Category`,
    `Region`,
    `Inventory Level`,
    `Units Sold`,
    `Units Ordered`,
    `Price`,
    `Discount`,
    `Weather Condition`,
    `Promotion`,
    `Competitor Pricing`,
    `Seasonality`,
    `Epidemic`,
    `Demand`
FROM updated_sales_data;

select * from sales_analysis limit 10;

describe sales_analysis;



#what is the overall sales performance of the business
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT `Product ID`) AS total_products,
    COUNT(DISTINCT `Store ID`) AS total_stores,
    SUM(`Units Sold`) AS total_units_sold,
    SUM(`Units Ordered`) AS total_units_ordered,
    ROUND(AVG(`Price`), 2) AS average_price,
    ROUND(AVG(`Discount`), 2) AS average_discount
FROM updated_sales_data;


#Which categories contribute the most to total sales volume?
SELECT Category, 
       SUM(`Units Sold`) AS total_units_sold, 
       COUNT(DISTINCT `Product ID`) AS total_products, 
       ROUND(AVG(Price), 2) AS average_price
FROM updated_sales_data
GROUP BY Category
ORDER BY total_units_sold DESC;


#What are the top 10 best-selling products?
SELECT `Product ID`, Category,
      SUM(`Units Sold`) AS total_units_sold,
      ROUND(AVG(Price), 2) AS average_price,
      SUM(`Units Ordered`) AS total_units_ordered
FROM updated_sales_data
GROUP BY `Product ID`, Category
ORDER BY total_units_sold DESC
LIMIT 10;



#Which product has the lowest sales?
SELECT `Product ID`, Category, 
       SUM(`Units Sold`) AS total_units_sold,  
       COUNT(DISTINCT `Date`) AS active_days
FROM updated_sales_data
GROUP BY `Product ID`, Category
ORDER BY total_units_sold ASC
LIMIT 10;



#Which products should be reordered first?

WITH product_metrics AS (
    SELECT
        `Store ID`,
        `Product ID`,
        MAX(`Inventory Level`) AS inventory_level,
        AVG(`Units Sold`) AS avg_daily_sales
    FROM sales
    GROUP BY `Store ID`, `Product ID`
)
SELECT
    `Store ID`,
    `Product ID`,
    inventory_level,
    ROUND(avg_daily_sales, 2) AS avg_daily_sales,
    ROUND(
        inventory_level / NULLIF(avg_daily_sales, 0), 2
    ) AS estimated_days_of_stock
FROM product_metrics
WHERE avg_daily_sales > 0
ORDER BY estimated_days_of_stock ASC;




#Are sales increasing or decreasing month by month?
WITH monthly_sales AS (
    SELECT
        DATE_FORMAT(`Date`, '%Y-%m') AS sales_month,
        SUM(`Units Sold`) AS total_units
    FROM updated_sales_data
    GROUP BY DATE_FORMAT(`Date`, '%Y-%m')
),
sales_trend AS (
    SELECT
        sales_month,
        total_units,
        LAG(total_units) OVER (
            ORDER BY sales_month
        ) AS previous_month_units
    FROM monthly_sales
)
SELECT
    sales_month,
    total_units,
    previous_month_units,
    ROUND(
        100.0 * (total_units - previous_month_units)
        / NULLIF(previous_month_units, 0),
        2
    ) AS mom_growth_pct
FROM sales_trend
ORDER BY sales_month;


# Which days of the week have the highest demand?
SELECT
    DAYNAME(`Date`) AS day_of_week,
    DAYOFWEEK(`Date`) AS day_number,
    SUM(`Units Sold`) AS total_units_sold,
    ROUND(AVG(`Units Sold`), 2) AS avg_units_per_record
FROM updated_sales_data
GROUP BY
    DAYNAME(`Date`),
    DAYOFWEEK(`Date`)
ORDER BY day_number;


#Where is our price higher than the competitor's?
SELECT
    `Product ID`,
    `Category`,
    ROUND(AVG(`Price`), 2) AS our_avg_price,
    ROUND(AVG(`Competitor Pricing`), 2)
        AS competitor_avg_price,
    ROUND(
        AVG(`Price` - `Competitor Pricing`), 2
    ) AS avg_price_difference
FROM updated_sales_data
WHERE `Competitor Pricing` IS NOT NULL
GROUP BY `Product ID`, `Category`
ORDER BY avg_price_difference DESC;



#Which products have declining sales?
WITH monthly_product_sales AS (
    SELECT
        `Product ID`,
        DATE_FORMAT(`Date`, '%Y-%m') AS sales_month,
        SUM(`Units Sold`) AS monthly_units
    FROM updated_sales_data
    GROUP BY
        `Product ID`,
        DATE_FORMAT(`Date`, '%Y-%m')
),
monthly_comparison AS (
    SELECT
        `Product ID`,
        sales_month,
        monthly_units,
        LAG(monthly_units) OVER (
            PARTITION BY `Product ID`
            ORDER BY sales_month
        ) AS previous_month_units
    FROM monthly_product_sales
)
SELECT
    `Product ID`,
    sales_month,
    monthly_units,
    previous_month_units,
    ROUND(
        100.0 * (monthly_units - previous_month_units)
        / NULLIF(previous_month_units, 0),
        2
    ) AS growth_pct
FROM monthly_comparison
WHERE previous_month_units IS NOT NULL
  AND monthly_units < previous_month_units
ORDER BY growth_pct ASC;



#Which products are potentially overstocked?
WITH daily_sales AS (
    SELECT
        `Store ID`,
        `Product ID`,
        sales_date,
        SUM(`Units Sold`) AS daily_units
    FROM sales_analysis
    GROUP BY `Store ID`, `Product ID`, sales_date
),
avg_sales AS (
    SELECT
        `Store ID`,
        `Product ID`,
        AVG(daily_units) AS avg_daily_sales
    FROM daily_sales
    GROUP BY `Store ID`, `Product ID`
),
latest_stock AS (
    SELECT
        `Store ID`,
        `Product ID`,
        `Inventory Level`,
        ROW_NUMBER() OVER (
            PARTITION BY `Store ID`, `Product ID`
            ORDER BY sales_date DESC
        ) AS rn
    FROM sales_analysis
)
SELECT
    s.`Store ID`,
    s.`Product ID`,
    s.`Inventory Level`,
    ROUND(a.avg_daily_sales, 2) AS avg_daily_sales,
    ROUND(
        s.`Inventory Level` / NULLIF(a.avg_daily_sales, 0), 2
    ) AS stock_coverage_days
FROM latest_stock s
JOIN avg_sales a
    ON s.`Store ID` = a.`Store ID`
    AND s.`Product ID` = a.`Product ID`
WHERE s.rn = 1
  AND a.avg_daily_sales > 0
  AND s.`Inventory Level` / a.avg_daily_sales > 10
ORDER BY stock_coverage_days DESC;




#Which seasons generate the highest demand?
SELECT
    Seasonality,
    SUM(`Units Sold`) AS total_units_sold,
    ROUND(AVG(`Units Sold`), 2) AS average_units_sold,
    COUNT(*) AS total_records
FROM updated_sales_data
GROUP BY Seasonality
ORDER BY total_units_sold DESC;



#Do promotions increase product sales?

SELECT
    Promotion,
    COUNT(*) AS observations,
    SUM(`Units Sold`) AS total_units_sold,
    ROUND(AVG(`Units Sold`), 2) AS average_units_sold,
    ROUND(AVG(Price), 2) AS average_price
FROM updated_sales_data
GROUP BY Promotion
ORDER BY average_units_sold DESC;



#Which products have unusually high sales spikes?
WITH product_statistics AS (
    SELECT
        `Store ID`,
        `Product ID`,
        AVG(`Units Sold`) AS avg_sales,
        STDDEV_POP(`Units Sold`) AS sales_std_dev
    FROM updated_sales_data
    GROUP BY `Store ID`, `Product ID`
)
SELECT
    s.`Date`,
    s.`Store ID`,
    s.`Product ID`,
    s.`Units Sold`,
    ROUND(p.avg_sales, 2) AS average_sales,
    ROUND(p.sales_std_dev, 2) AS sales_std_dev,
    'Unusual Sales Spike' AS alert
FROM updated_sales_data s
JOIN product_statistics p
    ON s.`Store ID` = p.`Store ID`
    AND s.`Product ID` = p.`Product ID`
WHERE s.`Units Sold` > p.avg_sales + (2 * p.sales_std_dev)
ORDER BY s.`Units Sold` DESC;



#Which products have the highest potential revenue?
SELECT
    `Product ID`,
    Category,
    SUM(`Units Sold`) AS total_units_sold,
    ROUND(AVG(Price), 2) AS average_price,
    ROUND(
        SUM(`Units Sold` * Price), 2
    ) AS estimated_gross_sales
FROM updated_sales_data
GROUP BY `Product ID`, Category
ORDER BY estimated_gross_sales DESC
LIMIT 10;


#Which products have the highest potential revenue?
SELECT
    `Store ID`,
    Region,
    SUM(`Inventory Level`) AS total_inventory,
    SUM(`Units Sold`) AS total_units_sold,
    ROUND(
        SUM(`Inventory Level`) /
        NULLIF(SUM(`Units Sold`), 0), 2
    ) AS inventory_to_sales_ratio
FROM updated_sales_data
GROUP BY `Store ID`, Region
ORDER BY inventory_to_sales_ratio DESC;