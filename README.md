📊 Retail Order Data Analysis

This project is a Streamlit web application that performs a comprehensive analysis on a retail orders dataset sourced from Kaggle. It loads the data from a CSV file, stores it in a PostgreSQL database, and provides interactive visualizations using Plotly to derive business insights.



📁 Dataset Source
Kaggle Dataset: Retail Orders - by ankitbansal06

Download command:
!kaggle datasets download ankitbansal06/retail-orders -f orders.csv



🏗️ Project Structure

├── orders.csv                # Dataset downloaded from Kaggle

├── main.py                    # Main Streamlit application

├── README.md                 # This documentation file



⚙️ Setup Instructions
1. Install Python Dependencies
pip install pandas sqlalchemy psycopg2 streamlit plotly kaggle

Ensure you have a valid kaggle.json API token set up if you're using the Kaggle CLI to download the dataset.




2. Set Up PostgreSQL
host = 'localhost'
user = 'postgres'
password = 'yourpassword'
database = 'mdte16db'



3. Download the Dataset
kaggle datasets download ankitbansal06/retail-orders -f orders.csv


🚀 How to Run
streamlit run main.py


🧠 Dashboard Features – 20 Key Business Questions Answered

1. Top 10 revenue-generating products
2. Cities with the highest profit margin
3. Category-wise total discount
4. Category-wise average sale price
5. Region-wise average sales price
6. Total profit by product category
7. Top 3 segments with highest quantity of orders
8. Average discount percentage by region
9. Sub-category with highest profit
10. Annual total revenue
11. Top 10 states by sales percentage
12. Month-wise year-over-year (YoY) sales growth
13. Top 5 profit months
14. Monthly total discount
15. Segment-wise discount analysis
16. State-wise total profit
17. Top 5 discount-heavy cities
18. States with highest average sale price
19. Low-margin sub-categories (<10%)
20. Order-level profit categorization (High/Medium/Low)


📬 Feedback
Open to suggestions, issues, and pull requests to improve functionality or extend analytics.
