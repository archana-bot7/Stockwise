import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import pickle, json
import plotly.express as px

ROOT=Path(__file__).parent
DATA=ROOT/'data'/'stockwise_sales.csv'
MODEL=ROOT/'models'/'xgboost_stockwise_model.pkl'
META=ROOT/'models'/'encoding_classes.json'
SQL=ROOT/'sql'/'stockwise_analytics.sql'
ASSETS=ROOT/'assets'

st.set_page_config(page_title='StockWise | Inventory Intelligence',page_icon='📦',layout='wide')

@st.cache_data
def load_data():
    d=pd.read_csv(DATA)
    d['Date']=pd.to_datetime(d['Date'],errors='coerce')
    return d.dropna(subset=['Date','Product ID'])
@st.cache_resource
def load_model():
    with open(MODEL,'rb') as f: m=pickle.load(f)
    with open(META) as f: enc=json.load(f)
    return m,enc

@st.cache_data
def load_demand_features(by_individual_product=False):
    d=load_data()
    if by_individual_product:
        stats=(
            d.groupby(['Product', 'Product ID', 'Category'], dropna=False)['Units Sold']
            .agg(
                Average_Daily_Sales='mean',
                Total_Units_Sold='sum',
                Sales_Std='std',
            )
            .reset_index()
            .rename(columns={'Product':'Product Name'})
        )
    else:
        product_names_map=(
            d.groupby('Product ID')['Product']
            .apply(lambda s: ', '.join(dict.fromkeys(s)))
            .to_dict()
        )
        stats=(
            d.groupby('Product ID', dropna=False)['Units Sold']
            .agg(
                Average_Daily_Sales='mean',
                Total_Units_Sold='sum',
                Sales_Std='std',
            )
            .reset_index()
        )
        stats['Product Name']=stats['Product ID'].map(product_names_map)
    stats['Demand_CV']=(
        stats['Sales_Std']/
        stats['Average_Daily_Sales'].replace(0,np.nan)
    )
    high_threshold=stats['Average_Daily_Sales'].quantile(0.75)
    low_threshold=stats['Average_Daily_Sales'].quantile(0.25)
    stats['Demand_Level']=np.select(
        [
            stats['Average_Daily_Sales'] >= high_threshold,
            stats['Average_Daily_Sales'] <= low_threshold,
        ],
        ['High Demand', 'Low Demand'],
        default='Medium Demand',
    )
    stats['Demand_Pattern']=np.where(
        stats['Demand_CV'] > 0.5,
        'Irregular Demand',
        'Relatively Stable Demand',
    )
    return stats.sort_values('Average_Daily_Sales', ascending=False).reset_index(drop=True)

df=load_data()
page=st.sidebar.radio('NAVIGATION',['Overview','ML Forecasting','Power BI Dashboard','SQL Analytics','Documentation'])
st.sidebar.markdown('---')
st.sidebar.caption('StockWise · Demand forecasting & inventory optimization')

if page=='Overview':
    st.title('📦 STOCKWISE')
    st.subheader('Smart Demand Forecasting & Inventory Optimization')
    st.write('A data-driven retail inventory project combining Python preprocessing, SQL business analytics, XGBoost demand prediction and reorder planning.')
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Sales records',f'{len(df):,}')
    c2.metric('Products',f'{df["Product"].nunique():,}')
    c3.metric('Stores',f'{df["Store ID"].nunique():,}')
    c4.metric('Units sold',f'{df["Units Sold"].sum():,}')
    demand_stats=load_demand_features()
    d1,d2,d3,d4=st.columns(4)
    d1.metric('Avg. daily sales',f'{demand_stats["Average_Daily_Sales"].mean():.1f}')
    d2.metric('High-demand products',f'{(demand_stats["Demand_Level"] == "High Demand").sum():,}')
    d3.metric('Irregular demand products',f'{(demand_stats["Demand_Pattern"] == "Irregular Demand").sum():,}')
    d4.metric('Demand CV',f'{demand_stats["Demand_CV"].mean():.2f}')
    st.markdown('### Demand feature analysis from the notebook')
    view_mode = st.radio(
        'View breakdown:',
        ['Product ID with Product Names (Notebook)', 'Individual Products (64 Items)'],
        horizontal=True
    )
    if view_mode == 'Individual Products (64 Items)':
        ind_stats = load_demand_features(by_individual_product=True)
        top_products = ind_stats.head(10)[['Product ID','Product Name','Category','Average_Daily_Sales','Total_Units_Sold','Demand_CV','Demand_Level','Demand_Pattern']].copy()
        st.dataframe(top_products, use_container_width=True)
        chart_df = top_products.sort_values('Average_Daily_Sales', ascending=False)
        st.bar_chart(chart_df.set_index('Product Name')['Average_Daily_Sales'])
    else:
        top_products = demand_stats.head(10)[['Product ID','Product Name','Average_Daily_Sales','Total_Units_Sold','Demand_CV','Demand_Level','Demand_Pattern']].copy()
        st.dataframe(top_products, use_container_width=True)
        chart_df = top_products.sort_values('Average_Daily_Sales', ascending=False).copy()
        chart_df['Chart Label'] = chart_df['Product ID'] + ' - ' + chart_df['Product Name'].apply(lambda s: s.split(',')[0])
        st.bar_chart(chart_df.set_index('Chart Label')['Average_Daily_Sales'])
    st.markdown('### Project pipeline')
    st.info('CSV data → Python preprocessing & exploration → MySQL analytics → XGBoost demand prediction → inventory recommendations → Power BI')
    st.markdown('### What StockWise helps answer')
    a,b,c=st.columns(3)
    a.markdown('**📈 Demand**\n\nWhich products are expected to sell more?')
    b.markdown('**⏳ Stockout risk**\n\nHow many days might current stock last?')
    c.markdown('**🛒 Reordering**\n\nWhen should the shop reorder and how much?')
    st.caption('Dataset supplied for this project. Confirm its provenance and usage terms before public commercial use.')

elif page=='ML Forecasting':
    st.title('🤖 XGBoost Demand & Inventory Forecast')
    st.write('Choose a product and provide current operating inputs. The model predicts the dataset’s **Demand** target; inventory timing and reorder quantity are calculated from that prediction.')
    model,enc=load_model()
    # Show human-readable product names in the selector. The model still receives
    # the corresponding Product ID code expected by its training schema.
    product_options=(
        df[['Product','Product ID']]
        .dropna()
        .drop_duplicates()
        .sort_values('Product')['Product']
        .astype(str)
        .tolist()
    )
    product_name=st.selectbox('Select a product', product_options)
    row=(df[df['Product'].astype(str)==product_name]
         .sort_values('Date')
         .iloc[-1])
    product_id=str(row['Product ID'])
    st.caption(f"Selected item: **{product_name}** · {row['Category']} · SKU: {product_id}")
    with st.form('forecast_form'):
        x1,x2,x3=st.columns(3)
        date=x1.date_input('Forecast date',value=pd.Timestamp.today().date())
        inventory=x2.number_input('Current inventory (units)',min_value=0,value=int(row['Inventory Level']))
        ordered=x3.number_input('Units already ordered',min_value=0,value=int(row['Units Ordered']))
        x4,x5,x6=st.columns(3)
        sold=x4.number_input('Recent units sold (input)',min_value=0,value=int(row['Units Sold']))
        price=x5.number_input('Selling price',min_value=0.0,value=float(row['Price']),step=0.5)
        discount=x6.number_input('Discount (%)',min_value=0.0,max_value=100.0,value=float(row['Discount']),step=1.0)
        x7,x8,x9=st.columns(3)
        competitor=x7.number_input('Competitor pricing',min_value=0.0,value=float(row['Competitor Pricing']),step=0.5)
        season_options=enc['Seasonality']
        season=x8.selectbox('Seasonality',season_options,index=season_options.index(str(row['Seasonality'])) if str(row['Seasonality']) in season_options else 0)
        lead=x9.number_input('Supplier lead time (days)',min_value=1,max_value=90,value=8)
        x10,x11,x12=st.columns(3)
        safety=x10.number_input('Safety stock buffer (units)',min_value=0,value=50)
        review=x11.number_input('Review period (days)',min_value=1,max_value=60,value=7)
        submitted=st.form_submit_button('Predict demand & inventory plan',type='primary')
    if submitted:
        pclasses=enc['Product ID']; sclasses=enc['Seasonality']
        if product_id not in pclasses or season not in sclasses:
            st.error('This product or season was not present in the model encoding metadata.')
        else:
            features=pd.DataFrame([{
              'Product ID':pclasses.index(product_id),'Inventory Level':inventory,'Units Ordered':ordered,
              'Units Sold':sold,'Price':price,'Discount':discount,'Year':date.year,'Month':date.month,'Day':date.day,
              'Seasonality':sclasses.index(season),'Competitor Pricing':competitor
            }])
            try:
                pred=max(0.0,float(model.predict(features)[0]))
                daily_demand=pred
                days=inventory/daily_demand if daily_demand>0 else np.inf
                reorder_point=daily_demand*lead+safety
                inventory_position=inventory+ordered
                target=daily_demand*(lead+review)+safety
                qty=max(0,int(np.ceil(target-inventory_position)))
                m1,m2,m3,m4=st.columns(4)
                m1.metric('Predicted demand',f'{pred:,.1f} units')
                m2.metric('Estimated stock coverage', 'No depletion' if not np.isfinite(days) else f'{days:.1f} days')
                m3.metric('Reorder point',f'{reorder_point:,.1f} units')
                m4.metric('Suggested reorder',f'{qty:,} units')
                if inventory_position<=reorder_point: st.error('REORDER NOW — inventory position is at or below the reorder point.')
                else: st.success('Stock is currently above the reorder point under these assumptions.')
                st.caption('Calculation assumptions: predicted Demand is treated as a daily demand estimate; order quantity targets lead time + review period + safety stock. Validate this interpretation against the original model training and real supplier data before operational use.')
                chart=pd.DataFrame({'Day':range(0,int(min(np.ceil(days),60))+1),'Estimated stock': [max(0,inventory-daily_demand*d) for d in range(0,int(min(np.ceil(days),60))+1)]})
                st.plotly_chart(px.line(chart,x='Day',y='Estimated stock',title='Illustrative stock depletion at predicted demand'),use_container_width=True)
            except Exception as e: st.exception(e)
    with st.expander('Model details & feature schema'):
        st.write('The uploaded serialized XGBoost model expects 10 features: Product ID, Inventory Level, Units Ordered, Units Sold, Price, Year, Month, Day, Seasonality and Competitor Pricing.')
        st.write('Categorical codes are reconstructed from sorted unique values in the supplied CSV. The original LabelEncoder objects were not supplied, so this reconstruction assumes the training encoders were fitted on the same complete category sets.')

elif page=='Power BI Dashboard':
    st.title('📊 Power BI Business Dashboards')
    st.write('Executive business intelligence dashboards created in Power BI analyzing sales revenue, stock levels, product demand, and inventory health across stores.')

    tab1, tab2 = st.tabs([
        '📈 Profit, Revenue & Sales Analysis',
        '📦 Inventory Level & Demand Analysis'
    ])

    with tab1:
        st.subheader('Stock wise Profit, Revenue and Sales Analysis Dashboard')
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Total Units Sold', '7.0M')
        c2.metric('Total Revenue', '$455.30M')
        c3.metric('Unique Products', '20 SKUs')
        c4.metric('Top Selling Item', 'Peanut Butter')

        img1_path = ASSETS / 'powerbi_profit_revenue_sales.png'
        if img1_path.exists():
            st.image(str(img1_path), caption='Stock wise Profit, Revenue and Sales Analysis Dashboard', use_container_width=True)
            with open(img1_path, 'rb') as f:
                st.download_button('📥 Download Dashboard 1 (High Res)', data=f.read(), file_name='stockwise_profit_revenue_sales.png', mime='image/png')
        else:
            st.warning('Dashboard image not found in assets.')

        st.markdown('#### 🔍 Key Dashboard Insights')
        st.markdown('''
- **Seasonal Sales Leadership**: Groceries and Clothing generate consistent high sales volume across all four seasons (Summer, Winter, Autumn, Spring).
- **Store-Category Performance**: Stores **S003** and **S004** show the highest revenue contribution, especially in Groceries and Furniture.
- **Revenue Drivers**: Increased units sold and steady demand levels are the strongest statistical influencers driving total store revenue upwards.
- **Top 10 Products by Sales Volume**: Peanut Butter, Lentils (Dal), Wheat Flour, Biscuits, Basmati Rice, Coffee Powder, Cricket Set, Salt, Cooking Oil, and Tomato Ketchup.
        ''')

    with tab2:
        st.subheader('Stock wise Inventory Level and Demand Analysis Dashboard')
        d1, d2, d3, d4 = st.columns(4)
        d1.metric('Average Demand', '104.32')
        d2.metric('Total Units Ordered', '7.0M')
        d3.metric('Total Stock Reserves', '23.0M')
        d4.metric('Highest Stock Category', 'Groceries (47.9%)')

        img2_path = ASSETS / 'powerbi_inventory_demand.png'
        if img2_path.exists():
            st.image(str(img2_path), caption='Stock wise Inventory Level and Demand Analysis Dashboard', use_container_width=True)
            with open(img2_path, 'rb') as f:
                st.download_button('📥 Download Dashboard 2 (High Res)', data=f.read(), file_name='stockwise_inventory_demand.png', mime='image/png')
        else:
            st.warning('Dashboard image not found in assets.')

        st.markdown('#### 🔍 Key Dashboard Insights')
        st.markdown('''
- **Inventory Allocation**: Groceries represent nearly half of all stock holdings (**47.87% / 11M units**), followed by Clothing (**15%**), Furniture (**14.9%**), Electronics (**11.6%**), and Toys (**10.7%**).
- **Store Inventory Distribution**: Stores **S002 (5.05M)** and **S003 (4.89M)** maintain the highest stock reserves to guard against stockouts.
- **Demand Decomposition Tree**: Breaks down **7.93M total customer demand** dynamically across Categories, Seasons, and Price points.
- **Reorder Pipeline**: Funnel analytics track 7M ordered replenishment units across product categories to align supply with seasonal peaks.
        ''')

elif page=='SQL Analytics':
    st.title('🗄️ SQL Business Analytics')
    st.write('Explore the SQL questions and queries used for StockWise business analysis. Query results are not executed here; connect a MySQL database to enable live results.')
    raw=SQL.read_text(encoding='utf-8') if SQL.exists() else '-- SQL file not found'
    sections=[]; current='General setup'; buf=[]
    for line in raw.splitlines():
        if line.strip().startswith('#'):
            if buf: sections.append((current,'\n'.join(buf).strip())); buf=[]
            current=line.strip('# ').strip() or 'SQL section'
        else: buf.append(line)
    if buf: sections.append((current,'\n'.join(buf).strip()))
    for title,query in sections:
        if query.strip():
            with st.expander(title): st.code(query,language='sql')
    st.download_button('Download SQL file',data=raw,file_name='stockwise_analytics.sql',mime='text/plain')

else:
    st.title('📘 Project Documentation')
    st.markdown('### Objective')
    st.write('StockWise explores retail sales and demand to support inventory planning, stockout-risk estimation and replenishment decisions.')
    st.markdown('### Technology stack')
    st.write('Python · Pandas · NumPy · XGBoost · MySQL · Power BI · Streamlit · Plotly')
    st.markdown('### Workflow')
    st.write('1. Load and inspect retail data. 2. Clean and prepare features. 3. Analyze business performance in SQL. 4. Predict the Demand target with XGBoost. 5. Estimate stock coverage, reorder point and order quantity. 6. Present insights in Power BI.')
    st.markdown('### Important assumptions and limitations')
    st.write('The supplied CSV does not include product purchase cost, so genuine gross profit margins cannot be calculated from the supplied fields alone. Stockout and reorder estimates depend on treating the model output as daily demand and on user-provided lead time and safety stock. The serialized model was supplied without its original LabelEncoder objects; category codes are reconstructed from the CSV and must be verified against the training environment.')
    st.markdown('### Source files')
    st.write('The repository includes the original notebook, supplied dataset, SQL queries and serialized XGBoost model.')
