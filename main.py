import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# read the csv file using pandas
orders_data = pd.read_csv("orders.csv")
# print(pd.DataFrame(orders_data))


# To understand the data types of the data set
# orders_data.info()


# Convert 'order date' from object to datetime
orders_data['Order Date'] = pd.to_datetime(orders_data['Order Date'])


# Find the null and nan values
print(orders_data.isnull().sum())
print(orders_data.isna().sum())
orders_data.info()


# Find missing value index
missing_index = pd.isna(orders_data['Ship Mode'])
missing_index = pd.isnull(orders_data['Ship Mode'])
print(orders_data[missing_index])


# Rename/Standardize column name
orders_data.rename(columns=
                   {
                   'Order Id':'order_id', 
                   'Order Date': 'order_date', 
                   'Ship Mode': 'ship_mode', 
                   'Segment':'segment', 
                   'Country':'country', 
                   'City':'city', 
                   'State':'state', 
                   'Postal Code':'postal_code', 
                   'Region':'region', 
                   'Category':'category', 
                   'Sub Category':'sub_category', 
                   'Product Id':'product_id', 
                   'cost price':'cost_price', 
                   'List Price': 'list_price', 
                   'Quantity':'quantity', 
                   'Discount Percent':'discount_percentage'
                   },
                   inplace=True)
# print(pd.DataFrame(orders_data))

# Fill null values
orders_data['ship_mode'] = orders_data['ship_mode'].fillna(orders_data['ship_mode'].mode()[0])
# print(orders_data.isna().sum())


# Removing white spaces from text fields
def white_space_remover(data_frame):
    for i in data_frame.columns:
        if data_frame[i].dtype == 'object':
            data_frame[i] = data_frame[i].str.strip()
        else:
            pass

white_space_remover(orders_data)
# print(pd.DataFrame(orders_data))


# Derive new columns discount, sale price, and profit
orders_data['discount'] = orders_data['list_price'] * orders_data['discount_percentage'] / 100
orders_data['sale_price'] = orders_data['list_price'] - orders_data['discount']
orders_data['profit'] = orders_data['sale_price'] - orders_data['cost_price']
# print(pd.DataFrame(orders_data))
shipping_details = pd.DataFrame(orders_data.iloc[0:,0:9])
order_details = pd.DataFrame(orders_data)
sales_details = order_details.loc[:, ['order_id','category','sub_category','product_id','cost_price','list_price','quantity','discount_percentage','discount','sale_price','profit']]
orders_data.info()



# connect to postgresql database
host = 'localhost'
user = 'postgres'
password = 'password'
database = 'mdte16db'

engine = create_engine(f"postgresql://{user}:{password}@{host}/{database}")

orders_shipping_details = "shipping_details"
sales_data = "sales_details"


shipping_details.to_sql(orders_shipping_details,engine,if_exists="replace",index=False)
sales_details.to_sql(sales_data,engine,if_exists="replace",index=False)


print("success")
connection = psycopg2.connect(
    host = 'localhost',
    user = 'postgres',
    password = 'password',
    database = 'mdte16db'
)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
mediator = connection.cursor()

mediator.execute('''alter table sales_details
                 alter column sale_price type
                 real''', connection)
mediator.execute('''alter table sales_details
                 alter column profit type
                 real''', connection)

st.title("Retail Order Data Analysis")

# Q1 highest revenue product
if st.button('Question 1: Show Top 10 Revenue Products'):
    mediator.execute('''select sub_category, ROUND(sum(quantity*sale_price)::numeric,2) as total_revenue 
                    from sales_details
                    group by sub_category
                    order by total_revenue desc 
                    limit 10''', 
                    connection)

# Fetch all the rows
    rows = mediator.fetchall()

# Extract the data into separate lists
    product_ids = [row[0] for row in rows]
    total_revenues = [row[1] for row in rows]

    

# Create the Plotly chart
    q1 = pd.DataFrame(rows, columns=['Product', 'Total Revenue'])
    fig = px.bar(q1, x='Product', y='Total Revenue', text='Total Revenue', title='Top 10 Highest Revenue Products')
    st.plotly_chart(fig)




# Q2 City with highest Profit Margin
if st.button('Question 2: Show Top 5 Cities by Profit Margin'):
    mediator.execute(''' select shipping_details.city, 
                    round(COALESCE(nullif(round(sum(quantity*profit)::numeric,2),0)
                    /nullif(round(sum(quantity*sale_price)::numeric,2),0),0)*100::numeric,2)
                    AS profit_margin
                    from shipping_details inner join sales_details on
                    shipping_details.order_id = sales_details.order_id
                    GROUP BY shipping_details.city
                    ORDER BY profit_margin DESC
                    LIMIT 5''',
                    connection)
    Q_2 = mediator.fetchall()
    cities = [row[0] for row in Q_2]
    profit_margins = [row[1] for row in Q_2]
    fig = px.bar(x=cities, y=profit_margins, text=profit_margins, title='Top 5 Cities by Profit Margin')
    fig.update_xaxes(title_text='City')
    fig.update_yaxes(title_text='Profit Margin (%)')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)
        

#Q3 Category-wise Total Discount 
if st.button('Question 3: Show Category-wise Total Discount'):
    mediator.execute('''select category, round(sum(quantity*discount)::numeric,0) as category_wise_total_discount 
                    from sales_details
                    group by category''',
                    connection)

    Q_3 = mediator.fetchall()
    categories = [row[0] for row in Q_3]
    discounts = [row[1] for row in Q_3]
    fig = px.bar(x=categories, y=discounts, text=discounts, title='Category-wise Total Discount')
    fig.update_xaxes(title_text='Category')
    fig.update_yaxes(title_text='Total Discount')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

# Q4 Product Category_wise Average Sale Price
if st.button('Question 4: Show Category-wise Average Sale Price'):
    mediator.execute('''select category, 
    round((sum(quantity*sale_price)/sum(quantity))::numeric,2) as categorywise_average_price 
    from sales_details
    group by category
    order by categorywise_average_price desc''',
    connection)

    Q_4 = mediator.fetchall()
    categories = [row[0] for row in Q_4]
    average_prices = [row[1] for row in Q_4]
    fig = px.bar(x=categories, y=average_prices, title='Category-wise Average Sale Price')
    fig.update_xaxes(title_text='Category')
    fig.update_yaxes(title_text='Average Sale Price')
    fig.update_layout(xaxis_tickangle=-45)
    fig.update_traces(textposition='outside', texttemplate='%{y:.2f}')
    st.plotly_chart(fig)

# Q5 Region_wise Average Sales Price
if st.button('Question 5: Show Region-wise Average Sales Price'):
    mediator.execute('''select shipping_details.region, 
                    round((sum(quantity*sale_price)/sum(quantity))::numeric,2)
                    AS regionwise_average_price
                    from shipping_details 
                    inner join sales_details 
                    on shipping_details.order_id = sales_details.order_id
                    GROUP BY shipping_details.region
                    ORDER BY regionwise_average_price DESC''',
                    connection)
    Q_5 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_5, columns=['Region', 'Region-wise Average Price'])

    # Create a Plotly bar chart
    fig = px.bar(df, x='Region', y='Region-wise Average Price', text='Region-wise Average Price')
    fig.update_layout(title='Region-wise Average Sales Price',
                       xaxis_title='Region',
                       yaxis_title='Average Sales Price')

    # Show the plot
    st.plotly_chart(fig)

# Q6 Category_wise Total Profit
if st.button('Question 6: Show Category-wise Total Profit'):
    mediator.execute('''select category, 
                    round(sum(quantity*profit)::numeric,0) as categorywise_profit 
                    from sales_details
                    group by category
                    order by categorywise_profit desc''',
                    connection)
    Q_6 = mediator.fetchall()
     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_6, columns=['Category', 'Category-wise Total Profit'])

    # Create a Plotly bar chart
    fig = px.bar(df, x='Category', y='Category-wise Total Profit', text='Category-wise Total Profit')
    fig.update_layout(title='Category-wise Total Profit',
                       xaxis_title='Category',
                       yaxis_title='Total Profit')

    # Show the plot
    st.plotly_chart(fig)

# Q7 Top 3 Highest quantity of order
if st.button('Question 7: Show Top 3 Segments Highest Quantity of Order'):
    mediator.execute('''select shipping_details.segment, 
                    sum(quantity)
                    AS segmentwise_highest_order
                    from shipping_details 
                    inner join sales_details 
                    on shipping_details.order_id = sales_details.order_id
                    GROUP BY shipping_details.segment
                    ORDER BY segmentwise_highest_order DESC
                    limit 3''',
                    connection)
    
    Q_7 = mediator.fetchall()
     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_7, columns=['Segment', 'Segment-wise Highest Order'])

    # Create a Plotly bar chart
    fig = px.bar(df, x='Segment', y='Segment-wise Highest Order', text='Segment-wise Highest Order')
    fig.update_layout(title='Top 3 Highest Quantity of Order',
                       xaxis_title='Segment',
                       yaxis_title='Highest Order Quantity')

    # Show the plot
    st.plotly_chart(fig)

# Q8 Regionw_wise average discount perentage
if st.button('Question 8: Show Region-wise Average Discount Percentage'):
    mediator.execute('''select shipping_details.region, 
                    round(avg(discount_percentage)::numeric,2)
                    AS regionwise_avg_discount_percentage
                    from shipping_details 
                    inner join sales_details 
                    on shipping_details.order_id = sales_details.order_id
                    GROUP BY shipping_details.region
                    ORDER BY regionwise_avg_discount_percentage DESC''',
                    connection)

    Q_8 = mediator.fetchall()
    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_8, columns=['Region', 'Region-wise Average Discount Percentage'])

    # Create a Plotly pie chart
    fig = px.pie(df, names='Region', values='Region-wise Average Discount Percentage')
    fig.update_layout(title='Region-wise Average Discount Percentage')

    # Show the plot
    st.plotly_chart(fig)



# Q9 Highest profit category
if st.button('Question 9: Show Highest Profit Category'):
    mediator.execute('''select sub_category, round(sum(quantity*profit)::numeric,0) as highest_profit_category 
                    from sales_details
                    group by sub_category
                    order by highest_profit_category desc
                    limit 1''',
                    connection)

    Q_9 = mediator.fetchall()

    df = pd.DataFrame(Q_9, columns=['Sub-Category', 'Highest Profit Category'])

    # Display the table
    st.table(df)

mediator.execute('''select category, round(sum(quantity*profit)::numeric,0) as highest_profit_category 
                 from sales_details
                 group by category
                 order by highest_profit_category desc
                 limit 1''',
                 connection)



# Q10 Total revenue per year
if st.button('Question 10: Show Total Revenue per Year'):
    mediator.execute('''select extract('year' from order_date) as year, 
                    round(sum(quantity*sale_price)::numeric,0) as total_revenue 
                    from shipping_details
                    inner join sales_details
                    on shipping_details.order_id = sales_details.order_id
                    group by year''',
                    connection)

    Q_10 = mediator.fetchall()

     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_10, columns=['Year', 'Total Revenue'])

    # Create a Plotly bar chart
    fig = px.bar(df, x='Year', y='Total Revenue', text='Total Revenue')
    fig.update_layout(title='Total Revenue per Year',
                       xaxis_title='Year',
                       yaxis_title='Total Revenue')

    # Show the plot
    st.plotly_chart(fig)

# Q11 Top 10 state with highest % of sales
if st.button('Question 11: Show Top 10 States with Highest % of Sales'):
    mediator.execute('''select shipping_details.state, 
                    round(round(sum(quantity*sale_price)::numeric,2)/
                    (select round(sum(quantity*sale_price)::numeric,2)
                    from sales_details) *100::numeric,2)
                    as percentage_of_sales
                    from shipping_details
                    inner join sales_details
                    on shipping_details.order_id = sales_details.order_id
                    group by shipping_details.state
                    order by percentage_of_sales desc
                    limit 10''',
                    connection)

    Q_11 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_11, columns=['State', 'Percentage of Sales'])

    # Create a Plotly horizontal bar chart
    fig = px.bar(df, x='Percentage of Sales', y='State', text='Percentage of Sales', orientation='h')
    fig.update_layout(title='Top 10 States with Highest % of Sales',
                       xaxis_title='Percentage of Sales',
                       yaxis_title='State')

    # Show the plot
    st.plotly_chart(fig)

# Q12 Month wise YOY Sales Growth
if st.button('Question 12: Show Month-wise YOY Sales Growth'):
    mediator.execute('''SELECT 
  TO_CHAR(order_date, 'Month') AS month_name, 
  EXTRACT(YEAR FROM order_date) AS year, 
  ROUND(SUM(quantity*sale_price)::NUMERIC, 2) AS total_revenue,
  ROUND(
    ((ROUND(SUM(quantity*sale_price)::NUMERIC, 2) - 
      LAG(ROUND(SUM(quantity*sale_price)::NUMERIC, 2), 12) OVER 
        (ORDER BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date))) / 
     LAG(ROUND(SUM(quantity*sale_price)::NUMERIC, 2), 12) OVER 
       (ORDER BY EXTRACT(YEAR FROM order_date), EXTRACT(MONTH FROM order_date))) * 100::NUMERIC, 
    2
  ) AS yoy_growth
FROM 
  shipping_details
JOIN 
  sales_details 
  ON shipping_details.order_id = sales_details.order_id
GROUP BY 
  TO_CHAR(order_date, 'Month'), 
  EXTRACT(YEAR FROM order_date), 
  EXTRACT(MONTH FROM order_date)
ORDER BY 
  EXTRACT(MONTH FROM order_date);''', connection)

    Q_12 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_12, columns=['Month', 'Year', 'Total Revenue', 'YOY Growth'])

    # Display the DataFrame as a table
    st.write(df)

# Q13 Top 5 highest profit Month with revenue
if st.button('Question 13: Show Top 5 Highest Profit Months'):
    mediator.execute('''SELECT 
                TO_CHAR(order_date, 'Month-YYYY') AS month_year, 
                ROUND(SUM(quantity*profit)::NUMERIC, 2) AS total_profit
                FROM shipping_details
                JOIN sales_details 
                ON shipping_details.order_id = sales_details.order_id
                GROUP BY month_year 
                ORDER BY total_profit desc
                limit 5''',
                connection)

    Q_13 = mediator.fetchall()

      # Create a Pandas DataFrame
    df = pd.DataFrame(Q_13, columns=['Month-Year', 'Total Profit'])

    # Create a Plotly pie chart
    fig = px.pie(df, values='Total Profit', names='Month-Year')
    fig.update_layout(title='Top 5 Highest Profit Months')
    fig.update_traces(textinfo='label+percent', textposition='inside')

    # Show the plot
    st.plotly_chart(fig)

# Q14 Total discount given for each month
if st.button('Question 14: Show Total Discount Given for Each Month'):
    mediator.execute('''SELECT 
                TO_CHAR(order_date, 'Month-YYYY') AS month_year, 
                ROUND(SUM(quantity*discount)::NUMERIC, 0) AS total_discount
                FROM shipping_details
                JOIN 
                sales_details 
                ON shipping_details.order_id = sales_details.order_id
                GROUP BY 
                month_year 
                ORDER BY 
                total_discount desc''',
                connection)

    Q_14 = mediator.fetchall()

# Create a Pandas DataFrame
    df = pd.DataFrame(Q_14, columns=['Month-Year', 'Total Discount'])

    # Create a Plotly bar chart
    fig = px.bar(df, x='Month-Year', y='Total Discount', text='Total Discount')
    fig.update_layout(title='Total Discount Given for Each Month',
                       xaxis_title='Month-Year',
                       yaxis_title='Total Discount')

    # Show the plot
    st.plotly_chart(fig)

# Q15 segment wise discount details
if st.button('Question 15: Show Segment-wise Discount Details'):
    mediator.execute('''SELECT segment,
                ROUND(SUM(quantity*discount)::NUMERIC, 0) AS total_discount
                FROM shipping_details
                JOIN sales_details ON shipping_details.order_id = sales_details.order_id
                GROUP BY segment
                ORDER BY total_discount desc
                ''',connection)

    Q_15 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_15, columns=['Segment', 'Total Discount'])

    # Create a Plotly pie chart
    fig = px.pie(df, values='Total Discount', names='Segment')
    fig.update_layout(title='Segment-wise Discount Details')
    fig.update_traces(textinfo='label+percent', textposition='inside')

    # Show the plot
    st.plotly_chart(fig)

# Q16 Top 10 State wise total profit
if st.button('Question 16: Show State-wise Total Profit'):
    mediator.execute('''select shipping_details.state, 
                round(sum(quantity*profit)::numeric,0)
                as statewise_total_profit
                from shipping_details
                inner join sales_details
                on shipping_details.order_id = sales_details.order_id
                group by shipping_details.state
                order by statewise_total_profit desc
                limit 10
                ''',connection)

    Q_16 = mediator.fetchall()

     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_16, columns=['State', 'Total Profit'])

    fig = px.bar(df, x='State', y='Total Profit', text='Total Profit')
    fig.update_layout(
        title='State-wise Total Profit Ranking Chart',
        xaxis_title='State',
        yaxis_title='Total Profit'
    )

    # Show the plot
    st.plotly_chart(fig)


# Q17 Top 5 city with highest total discount 
if st.button('Question 17: Show Top 5 Cities with Highest Total Discount'):
    mediator.execute('''SELECT city,
                ROUND(SUM(quantity*discount)::NUMERIC, 0) AS total_discount
                FROM shipping_details
                JOIN sales_details ON shipping_details.order_id = sales_details.order_id
                GROUP BY city
                ORDER BY total_discount desc
                limit 5''',
                connection)

    Q_17 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_17, columns=['City', 'Total Discount'])

    # Create a pie chart
    fig = px.pie(df, values='Total Discount', names='City')
    fig.update_traces(textinfo='label+percent', textposition='inside')
    fig.update_layout(
        title='Top 5 Cities with Highest Total Discount'
    )

    # Show the plot
    st.plotly_chart(fig)

# Q18 Top 5 state with highest average sales price 
if st.button('Question 18: Show Top 5 States with Highest Average Sales Price'):
    mediator.execute('''select shipping_details.state, 
                    round((sum(quantity*sale_price)/sum(quantity))::numeric,2)
                    AS statewise_average_price
                    from shipping_details 
                    inner join sales_details 
                    on shipping_details.order_id = sales_details.order_id
                    GROUP BY shipping_details.state
                    ORDER BY statewise_average_price DESC
                    limit 5
                    ''',
                    connection)


    Q_18 = mediator.fetchall()

    # Create a Pandas DataFrame
    df = pd.DataFrame(Q_18, columns=['State', 'State-wise Average Price'])

     # Create a bar chart with a line
    fig = px.bar(df, x='State', y='State-wise Average Price', text='State-wise Average Price')
    fig.add_scatter(x=df['State'], y=df['State-wise Average Price'], mode='lines+markers', marker=dict(size=10))
    fig.update_layout(
        title='Top 5 States with Highest Average Sales Price',
        xaxis_title='State',
        yaxis_title='State-wise Average Price'
    )

    # Show the plot
    st.plotly_chart(fig)

# Q19 sub_category with less than 10% profit margin 
if st.button('Question 19: Show Sub-Categories with Less Than 10% Profit Margin'):
    mediator.execute(''' SELECT sub_category, 
                    ROUND(COALESCE(
                    NULLIF(ROUND(SUM(quantity*profit)::NUMERIC, 2), 0) / 
                    NULLIF(ROUND(SUM(quantity*sale_price)::NUMERIC, 2), 0), 
                    0) * 100::NUMERIC, 2) AS lowest_profit_margin
                    FROM sales_details
                    GROUP BY sub_category
                    HAVING ROUND(COALESCE(NULLIF(ROUND(SUM(quantity*profit)::NUMERIC, 2), 0) / 
                    NULLIF(ROUND(SUM(quantity*sale_price)::NUMERIC, 2), 0), 0) 
                    * 100::NUMERIC, 2
                    ) < 10
                    order by lowest_profit_margin;''',
                    connection)

    Q_19 = mediator.fetchall()

     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_19, columns=['Sub-Category', 'Lowest Profit Margin'])

    # Create a bar chart
    fig = px.bar(df, x='Sub-Category', y='Lowest Profit Margin', text='Lowest Profit Margin')
    fig.update_layout(
        title='Sub-Categories with Less Than 10% Profit Margin',
        xaxis_title='Sub-Category',
        yaxis_title='Lowest Profit Margin'
    )

    # Show the plot
    st.plotly_chart(fig)

# Q20 Order id and product category with profit ranking
if st.button('Question 20:Show Order ID and Product Category with Profit Ranking'):
    mediator.execute(''' WITH ranked_orders AS (
                    SELECT order_id,sub_category, round(quantity * profit::numeric,2) AS total_profit,
                    PERCENT_RANK() OVER (ORDER BY quantity * profit DESC) AS profit_percentile
                    FROM sales_details)
                    SELECT order_id, sub_category, total_profit,
                    CASE 
                    WHEN profit_percentile <= 0.1 THEN 'High Profit'
                    WHEN profit_percentile <= 0.3 THEN 'Medium Profit'
                    ELSE 'Low Profit'
                    END AS profit_category
                    FROM ranked_orders
                    ORDER BY total_profit DESC;''',
                    connection)

    Q_20 = mediator.fetchall()

     # Create a Pandas DataFrame
    df = pd.DataFrame(Q_20, columns=['Order ID', 'Sub-Category', 'Total Profit', 'Profit Category'])

    # Display the table
    st.write(df)




connection.close()
