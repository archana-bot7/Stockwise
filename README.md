# StockWise — Smart Demand Forecasting & Inventory Optimization


**StockWise** is an end-to-end inventory management and business analytics project that integrates machine learning, SQL, and Power BI. It uses an XGBoost model to forecast product demand, monitor inventory levels, estimate when stock is likely to run out, and recommend timely restocking through automated reorder alerts. The project also includes SQL-based business analytics queries to extract meaningful insights from sales and inventory data, along with an interactive Power BI dashboard for visualizing key business metrics, identifying trends, and supporting data-driven decisions. Overall, StockWise aims to help businesses optimize inventory management, reduce stock shortages, and make smarter operational decisions.


## Pages
- Overview: project summary and dataset KPIs.
- ML Forecasting: XGBoost demand prediction and rule-based stock coverage/reorder calculations.
- Power BI Dashboard: executive dashboards covering profit, revenue, sales, inventory levels, and demand analysis.
- SQL Analytics: browsable supplied SQL queries.
- Documentation: workflow, tools, assumptions and limitations.

## Important model note
The supplied model expects 10 features: Product ID, Inventory Level, Units Ordered, Units Sold, Price, Year, Month, Day, Seasonality, Competitor Pricing. The original LabelEncoder objects were not supplied. This app reconstructs sorted category mappings from the complete CSV. Verify these mappings against the original training environment before relying on predictions.

## Files
- `data/stockwise_sales.csv`: supplied dataset.
- `models/xgboost_stockwise_model.pkl`: supplied trained model.
- `models/encoding_classes.json`: reconstructed category classes.
- `notebooks/stockwise.ipynb`: original notebook.
- `sql/stockwise_analytics.sql`: supplied SQL file.
