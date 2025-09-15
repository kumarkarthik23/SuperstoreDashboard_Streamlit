# 📊 Superstore Sales Dashboard – Streamlit Project

This project presents an **interactive data dashboard** developed using **Streamlit** to analyze and visualize sales performance data from a global Superstore. The goal is to deliver actionable insights for business users through a modern, intuitive web interface.

🔗 **Live App:** [kksuperstoredashboard.streamlit.app](https://kksuperstoredashboard.streamlit.app)

---

## 🧠 Project Objective

The objective of this project is to create a user-friendly BI (Business Intelligence) dashboard that enables stakeholders to:

- Monitor and compare key performance indicators (KPIs) over time
- Explore trends in sales, profit, order quantity, and shipment metrics
- Drill down by geography, product categories, and customer segments
- Understand regional and product-level performance visually

---

## 📁 Dataset Overview

The dashboard uses the [Sample Superstore Dataset](https://community.tableau.com/s/sample-superstore), a public dataset commonly used in retail analytics projects. It includes:

- **Orders Sheet**: Contains sales transactions, profit, categories, customer info, and dates (2014–2017)
- **Returns Sheet** *(optional)*: Identifies returned orders

---

## 🛠️ Tech Stack

| Component   | Purpose                        |
|-------------|--------------------------------|
| **Streamlit** | Web app interface and deployment |
| **Pandas**    | Data manipulation and filtering |
| **Plotly**    | Interactive charts and maps     |
| **OpenPyXL**  | Excel data reading              |

---

## 🔍 Dashboard Features

### 📌 KPI Summary Cards
Displays high-level business metrics with period-over-period comparisons:
- Total Sales Revenue
- Average Order Value
- Total Orders Placed
- Total Profit
- Profit Margin (%)
- Average Shipment Time

### 📊 Visual Insights
- **Sales Over Time**: Time-series plot with optional moving average
- **Top 10 Products by Sales**: Horizontal bar chart
- **Sales by Region**: US map with sales shading
- **Customizable Filters**: Region, State, Category, Sub-Category, Segment, Date range

### ⚠️ Alerts
If no period-over-period change is detected, a notification banner is displayed to indicate stable performance or data gaps.


HI GIT
