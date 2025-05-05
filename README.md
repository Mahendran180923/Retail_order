# 📊 Retail Order Data Analysis

A **Streamlit web application** that performs a comprehensive analysis of a retail orders dataset from Kaggle. The app loads data from a CSV file, stores it in a **PostgreSQL** database, and delivers interactive **Plotly visualizations** to uncover key business insights.

---

## 📁 Dataset Source

- **Kaggle Dataset:** [Retail Orders by ankitbansal06](https://www.kaggle.com/datasets/ankitbansal06/retail-orders)  
- **Download via CLI:**
  ```bash
  kaggle datasets download ankitbansal06/retail-orders
  ```

---

## 🏗️ Project Structure

```
├── orders.csv              # Dataset from Kaggle
├── main.py                 # Streamlit application
├── README.md               # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Install Dependencies

Make sure Python is installed, then run:

```bash
pip install pandas sqlalchemy psycopg2 streamlit plotly kaggle
```

> **Note:** Set up your `kaggle.json` API token to enable dataset download via Kaggle CLI.

### 2️⃣ Configure PostgreSQL

Update your PostgreSQL credentials in `main.py`:
```python
host = 'localhost'
user = 'postgres'
password = 'yourpassword'
database = 'yourdb'
```

### 3️⃣ Download the Dataset

```bash
kaggle datasets download ankitbansal06/retail-orders -f orders.csv
```

---

## 🚀 Run the App

```bash
streamlit run main.py
```

This will open the interactive dashboard in your browser.

---

## 🧠 Dashboard Features

The application answers **20 essential business questions** using dynamic visualizations:

| #  | Business Question |
|----|-------------------|
| 1  | Top 10 revenue-generating products |
| 2  | Cities with the highest profit margin |
| 3  | Category-wise total discount |
| 4  | Category-wise average sale price |
| 5  | Region-wise average sales price |
| 6  | Total profit by product category |
| 7  | Top 3 segments with highest quantity of orders |
| 8  | Average discount percentage by region |
| 9  | Sub-category with highest profit |
| 10 | Annual total revenue |
| 11 | Top 10 states by sales percentage |
| 12 | Month-wise year-over-year (YoY) sales growth |
| 13 | Top 5 profit months |
| 14 | Monthly total discount |
| 15 | Segment-wise discount analysis |
| 16 | State-wise total profit |
| 17 | Top 5 discount-heavy cities |
| 18 | States with highest average sale price |
| 19 | Low-margin sub-categories (<10%) |
| 20 | Order-level profit categorization (High/Medium/Low) |

---

## 💡 Technologies Used

- **Python**
- **Pandas**
- **SQLAlchemy**
- **PostgreSQL**
- **Streamlit**
- **Plotly**
- **Kaggle CLI**

---

## 📬 Feedback & Contributions

We're open to:
- Suggestions 💡
- Bug reports 🐞
- Pull requests 🚀

Feel free to fork the project, improve it, and share your insights!
