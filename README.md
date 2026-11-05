# StockWise — Smart Demand Forecasting & Inventory Optimization

**StockWise** is an end-to-end inventory management and business analytics project that integrates machine learning, SQL, and Power BI. It uses an XGBoost model to forecast product demand, monitor inventory levels, estimate when stock is likely to run out, and recommend timely restocking through automated reorder alerts. The project also includes SQL-based business analytics queries to extract meaningful insights from sales and inventory data, along with an interactive Power BI dashboard for visualizing key business metrics, identifying trends, and supporting data-driven decisions. Overall, StockWise aims to help businesses optimize inventory management, reduce stock shortages, and make smarter operational decisions.

## Pages
- Overview: project summary and dataset KPIs.
- ML Forecasting: XGBoost demand prediction and rule-based stock coverage/reorder calculations.
- Power BI Dashboard: executive dashboards covering profit, revenue, sales, inventory levels, and demand analysis.
- SQL Analytics: browsable supplied SQL queries.
- Documentation: workflow, tools, assumptions and limitations.


## 📌 1. Project Overview

Inventory management is an important part of running a successful business. Businesses need to maintain sufficient stock to meet customer demand while avoiding unnecessary inventory costs.

However, many businesses face challenges such as:

- Running out of popular products due to poor demand forecasting.
- Maintaining excess inventory that increases storage costs.
- Difficulty identifying products with high or low sales performance.
- Inefficient inventory replenishment planning.
- Lack of insights into historical sales and inventory trends.

**StockWise addresses these challenges using Data Analytics and Machine Learning.**

The project analyzes historical sales and inventory records to identify business trends, understand product performance, monitor stock levels, and predict future inventory requirements.

By integrating SQL-based analysis, Power BI dashboards, and an XGBoost prediction model, StockWise provides a data-driven approach to inventory management.

The ultimate goal is to help businesses make informed decisions about what to stock, when to reorder, and how much inventory they may need in the future.

## 🎯 2. Project Objectives

- Collect, clean, and preprocess raw sales and inventory datasets using Python.
- Perform exploratory data analysis to understand sales and inventory patterns.
- Use SQL queries to extract meaningful business insights from structured data.
- Analyze product demand, sales performance, and inventory availability.
- Develop interactive Power BI dashboards for business reporting and visualization.
- Build a machine learning model using XGBoost to forecast product demand.
- Estimate when existing inventory is likely to run out.
- Identify appropriate inventory replenishment timelines.
- Transform historical business data into actionable inventory management insights.

## ⚙️ 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning, manipulation, and preprocessing |
| NumPy | Numerical computations |
| Matplotlib | Data visualization |
| Seaborn | Exploratory data analysis and statistical visualization |
| MySQL | Database management and SQL-based business analysis |
| Power BI | Interactive dashboards and business intelligence |
| DAX | Calculated measures and analytical metrics |
| XGBoost | Machine learning and demand prediction |
| Scikit-learn | Model preparation and evaluation |
| Jupyter Notebook | Data analysis and experimentation |
| Git & GitHub | Version control and project management |

## 🐍 4. Data Preparation & Exploratory Data Analysis – Python

The first stage of StockWise focuses on preparing raw business data for further analysis.

Python is used to clean, transform, and organize the dataset to ensure that it is suitable for SQL analysis, visualization, and machine learning.

### Data Preparation Process

**Step 1: Data Loading**

Import the raw sales and inventory dataset into Python using Pandas.

**Step 2: Data Cleaning**

- Identify and handle missing values.
- Remove duplicate records where appropriate.
- Check and correct inconsistent data types.
- Handle inconsistent or invalid values.
- Ensure that numerical and categorical columns are properly formatted.

**Step 3: Data Transformation**

Prepare the dataset by organizing important business attributes, including:

- Store ID
- Product ID
- Category
- Region
- Date
- Inventory Level
- Units Sold
- Units Ordered
- Price
- Discount
- Weather Condition
- Promotion
- Competitor Pricing
- Seasonality
- Epidemic
- Demand

**Step 4: Exploratory Data Analysis (EDA)**

Explore the dataset to understand:

- Sales distribution across different products.
- Product demand patterns.
- Inventory availability.
- Seasonal variations in demand.
- Differences in sales performance across stores and regions.
- Relationships between business factors and product demand.

The cleaned dataset is then prepared for SQL-based analysis and machine learning.

## 🗄️ 5. Business Data Analysis – MySQL

After data preparation, the structured dataset is imported into MySQL for detailed business analysis.

SQL is used to extract meaningful information from the data through queries, aggregations, calculations, and analytical operations.

### Key SQL Analysis

**1. Sales Performance Analysis**

Analyze sales performance across different products, stores, categories, and regions.

**2. Product Demand Analysis**

Identify products with higher demand and analyze their sales patterns over time.

**3. Inventory Analysis**

Examine existing stock levels and understand the relationship between inventory availability and product sales.

**4. Daily Sales Analysis**

Calculate daily product sales to understand changing demand patterns.

**5. Average Daily Demand**

Calculate the average daily sales of individual products to estimate how quickly inventory is consumed.

**6. Stock Coverage Analysis**

Estimate how many days the available inventory can support based on average daily product demand.

**7. Replenishment Analysis**

Use inventory levels and demand patterns to identify products that may require restocking.

SQL transforms raw business records into structured analytical outputs that can be used for reporting and predictive modeling.

## 📊 6. Business Intelligence & Visualization – Power BI

Power BI is used to transform analytical data into interactive dashboards that provide a clear understanding of business performance.

The dashboards help users monitor important inventory and sales indicators without manually examining thousands of records.

### Dashboard Insights

**1. Sales Performance**

- Total sales and revenue analysis.
- Sales distribution across different product categories.
- Store-wise and regional sales performance.
- Product-level sales comparisons.

**2. Inventory Monitoring**

- Current inventory levels.
- Available stock across different products.
- Inventory distribution by category and store.
- Identification of products with potentially low inventory.

**3. Product Demand Analysis**

- Most demanded products.
- Products with lower sales activity.
- Demand patterns across different periods.
- Comparison of product demand across categories.

**4. Business Performance Overview**

- Key performance indicators (KPIs).
- Interactive filtering and drill-down analysis.
- Business trends through charts and visualizations.
- Data-driven insights for inventory planning.

The dashboard provides an organized view of business operations and helps decision-makers understand what is happening within their inventory and sales activities.

## 🤖 7. Machine Learning – Demand Forecasting Using XGBoost

One of the major components of StockWise is its machine learning model, developed using **XGBoost (Extreme Gradient Boosting)**.

The model uses historical business and inventory-related information to predict product demand.

XGBoost is a gradient boosting algorithm that builds multiple decision trees sequentially, where each new tree attempts to improve the predictions made by previous trees.

It is particularly useful for structured tabular datasets and can capture complex relationships between different business variables.

### Model Development Process

**Step 1: Feature Preparation**

Prepare relevant input features from the cleaned dataset, including historical sales, inventory levels, product information, and other demand-related variables.

**Step 2: Data Splitting**

Split the dataset into training and testing subsets to evaluate the model's ability to make predictions on unseen data.

**Step 3: Model Training**

Train the XGBoost regression model using historical business data to learn patterns associated with product demand.

**Step 4: Demand Prediction**

Use the trained model to estimate future product demand based on the available input features.

**Step 5: Inventory Planning**

Use predicted demand along with current inventory information and replenishment assumptions to estimate:

- How quickly the available inventory may be consumed.
- When the existing stock is likely to run out.
- When a product should be reordered.
- How inventory planning can be improved based on expected demand.

The objective is to move beyond simply analyzing historical sales and introduce predictive insights that can support future inventory decisions.

## 📦 8. Inventory Prediction & Replenishment Planning

StockWise extends demand forecasting into practical inventory planning.

Instead of only predicting how much a product may sell, the project uses demand predictions to estimate inventory requirements.

### Key Inventory Planning Capabilities

**1. Estimated Stock Exhaustion**

Estimate how many days the remaining inventory can support based on expected daily demand.

**2. Restocking Recommendations**

Estimate when inventory replenishment should take place to reduce the risk of stock shortages.

**3. Demand-Based Inventory Planning**

Use predicted product demand to support decisions about future stock requirements.

**4. Safety Stock Consideration**

Include a safety stock buffer to account for uncertainty in demand and reduce the risk of running out of inventory.

**5. Lead Time Consideration**

Account for the time required to receive new inventory after placing an order.

These calculations help translate machine learning predictions into practical inventory management decisions.

## 🔄 9. Complete Project Workflow

StockWise follows an end-to-end data analytics and machine learning pipeline.

```text
             RAW DATASET
                  |
                  ▼
        DATA COLLECTION
                  |
                  ▼
       DATA CLEANING & EDA
              (Python)
                  |
                  ▼
        DATA TRANSFORMATION
                  |
                  ▼
          MYSQL DATABASE
                  |
                  ▼
         SQL ANALYSIS
                  |
          ┌───────┴────────┐
          ▼                ▼
    BUSINESS ANALYSIS   FEATURE PREPARATION
          |                |
          ▼                ▼
     POWER BI          XGBOOST MODEL
     DASHBOARD          TRAINING
          |                |
          ▼                ▼
   BUSINESS INSIGHTS   DEMAND PREDICTION
                           |
                           ▼
                  INVENTORY PLANNING
                           |
                           ▼
                 RESTOCKING ESTIMATION
```



**StockWise – Turning Business Data into Smarter Inventory Decisions.** 📦
