# 📊 Superstore Sales Dashboard

An interactive business intelligence dashboard built with **Streamlit** to explore and analyze Superstore sales data across time, products, regions, and customer segments. Designed for data-driven decision-making, this tool offers dynamic filtering, KPI comparisons, and powerful visualizations using Plotly.

🚀 **Live Demo:** [Click to View Dashboard](https://kksuperstoredashboard.streamlit.app)

---

## 🌟 Key Features

- **KPI Cards**: Real-time insights on:
  - Total Sales Revenue  
  - Average Order Value  
  - Total Orders Placed  
  - Total Profit  
  - Profit Margin (%)  
  - Average Shipment Time  

- **Dynamic Filtering Panel**:
  - Region, State, Category, Sub-category, Customer Segment
  - Custom date range selection

- **Interactive Visuals**:
  - **Sales Over Time** with optional Moving Average
  - **Top 10 Products by Sales**
  - **Sales by Region (Choropleth Map)**

- **Period-over-Period Comparison**: Tracks % change across KPIs compared to past period (with no-change notification support)

---

## 📁 Dataset

- **Source**: [Sample Superstore Dataset](https://community.tableau.com/s/sample-superstore)
- Contains order-level transaction data from 2014–2017
- Two sheets used:
  - `Orders`: Sales, Profit, Quantity, Category, Segment, Date, Region
  - `Returns` (optional): Used to flag returned orders

---

## 🛠️ Tech Stack

- **Streamlit** – UI rendering and interactivity  
- **Pandas** – Data manipulation and aggregation  
- **Plotly Express** – Charts and map visualizations  
- **OpenPyXL** – Excel file handling  

---

## 🚀 Getting Started

### 🔧 Installation

```bash
pip install streamlit pandas plotly openpyxl
