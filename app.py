import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from datetime import timedelta

# ---- Set Page Configuration ----
st.set_page_config(
    page_title="SuperStore Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---- Custom CSS for Styling Borders & Underlines ----
st.markdown(
    """
    <style>
    div.block-container{padding-top:1rem; padding-bottom: 0px;}

    .title-test {
        font-weight: bold;
        font-size: 36px;
        padding: 5px;
        text-align: center;
    }

    .section-box {
        border: 2px solid #EAEAEA;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #FFFFFF;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1);
    }

    .section-header {
        font-weight: bold;
        font-size: 22px;
        border-bottom: 3px solid #007BFF;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    .kpi-box {
        background-color: #FFFFFF;
        border: 1px solid #D3D3D3;
        border-radius: 12px;
        padding: 14px;
        margin: 6px;
        text-align: center;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1);
    }

    .kpi-title {
        font-weight: 700;
        color: #333333;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-weight: 600;
        font-size: 24px;
        color: #007BFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Helper Functions ----
def format_number(value, decimals=1):
    """Format large numbers for display in KPI boxes"""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


@st.cache_data
def load_data():
    """Load and preprocess Superstore data with caching"""
    file_path = "Sample - Superstore.xlsx"

    # Load data efficiently
    df_orders = pd.read_excel(file_path, sheet_name="Orders", engine="openpyxl")
    df_returns = pd.read_excel(file_path, sheet_name="Returns", engine="openpyxl")

    # Convert 'Order Date' to datetime
    if not pd.api.types.is_datetime64_any_dtype(df_orders["Order Date"]):
        df_orders["Order Date"] = pd.to_datetime(df_orders["Order Date"])

    # Merge Returns Data
    returned_orders = set(df_returns["Order ID"])
    df_orders["Returned"] = df_orders["Order ID"].apply(lambda x: 1 if x in returned_orders else 0)

    # Calculate Margin Rate safely (Handle division by zero)
    df_orders["Margin Rate"] = (df_orders["Profit"] / df_orders["Sales"]).replace([float("inf"), -float("inf")], 0) * 100
    df_orders["Margin Rate"].fillna(0, inplace=True)

    # Ensure Ship Date is a valid datetime
    df_orders["Ship Date"] = pd.to_datetime(df_orders["Ship Date"], errors="coerce")
    
    # Calculate Shipment Time
    df_orders["Shipment Time"] = (df_orders["Ship Date"] - df_orders["Order Date"]).dt.days

    return df_orders

# ---- Load Data ----
df_original = load_data()

# ---- Page Header ----
col1, col2, col3 = st.columns([2, 8, 2])

with col1:
    st.empty()

with col2:
    st.markdown(
        """
        <div class="title-container">
            <h1 class="title-test">Superstore Sales Dashboard</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- Filters Section ----
with col3:
    st.markdown("<div style='display: flex; justify-content: flex-end; align-items: center; padding-top: 32px;'>",
                unsafe_allow_html=True)

    with st.popover("Open Filters"):
        st.markdown("### Filters")

        # Start with the full dataset
        df_filtered = df_original.copy()

        # Region Filter
        all_regions = sorted(df_original["Region"].dropna().unique())
        selected_region = st.selectbox("Select Region", options=["All"] + all_regions)

        if selected_region != "All":
            df_filtered = df_filtered[df_filtered["Region"] == selected_region]

        # State Filter
        all_states = sorted(df_filtered["State"].dropna().unique())
        selected_state = st.selectbox("Select State", options=["All"] + all_states)

        if selected_state != "All":
            df_filtered = df_filtered[df_filtered["State"] == selected_state]

        # Category Filter
        all_categories = sorted(df_filtered["Category"].dropna().unique())
        selected_category = st.selectbox("Select Category", options=["All"] + all_categories)

        if selected_category != "All":
            df_filtered = df_filtered[df_filtered["Category"] == selected_category]

        # Sub-Category Filter
        all_subcats = sorted(df_filtered["Sub-Category"].dropna().unique())
        selected_subcat = st.selectbox("Select Sub-Category", options=["All"] + all_subcats)

        if selected_subcat != "All":
            df_filtered = df_filtered[df_filtered["Sub-Category"] == selected_subcat]

        # Customer Segment Filter
        all_segments = sorted(df_filtered["Segment"].dropna().unique())
        selected_segment = st.selectbox("Select Customer Segment", options=["All"] + all_segments)

        if selected_segment != "All":
            df_filtered = df_filtered[df_filtered["Segment"] == selected_segment]

        # Handle empty dataset after filtering
        if df_filtered.empty:
            st.warning("No data available for the selected filters. Resetting to full dataset.")
            df_filtered = df_original.copy()

        # Date Range Filter
        min_date = df_filtered["Order Date"].min()
        max_date = df_filtered["Order Date"].max()

        # User selects date range
        from_date = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date)
        to_date = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date)

        # Auto-correct invalid date selections
        if from_date > to_date:
            st.warning("Invalid date range selected. Resetting to default range.")
            from_date, to_date = min_date, max_date

        # Apply Date Filter
        df_filtered = df_filtered[
            (df_filtered["Order Date"] >= pd.to_datetime(from_date)) &
            (df_filtered["Order Date"] <= pd.to_datetime(to_date))
        ]

    st.markdown("</div>", unsafe_allow_html=True)

# ---- Function to Compute KPIs ----
def compute_kpis(df):
    """Compute KPI metrics for a given dataset"""
    if df.empty:
        return 0, 0, 0, 0, 0, 0  # Return zeros if the dataframe is empty
    
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    avg_shipment_time = df["Shipment Time"].mean()
    avg_shipment_time = avg_shipment_time if not pd.isna(avg_shipment_time) else 0
    return total_sales, avg_order_value, total_orders, total_profit, profit_margin, avg_shipment_time

# ---- Handle Empty Dataset After Filters ----
if df_filtered.empty:
    st.warning("No data available for the selected filters. Showing full dataset.")
    df_filtered = df_original.copy()

# ---- Get Selected Date Range ----
from_date = pd.to_datetime(from_date)
to_date = pd.to_datetime(to_date)
date_range_days = (to_date - from_date).days

# ---- Determine Past Period Dynamically ----
past_start_date = from_date - timedelta(days=date_range_days)
past_end_date = to_date - timedelta(days=date_range_days)

# ---- Get Current and Past Data from a Single Filtered DataFrame ----
df_current = df_filtered[(df_filtered["Order Date"] >= from_date) & (df_filtered["Order Date"] <= to_date)]

# ---- Validate Past Date Range ----
df_min_date = df_original["Order Date"].min()
df_max_date = df_original["Order Date"].max()

# Check if past date range falls within available data
if past_start_date < df_min_date or past_end_date > df_max_date:
    df_past = pd.DataFrame(columns=df_original.columns)  # Empty DataFrame if out of range
else:
    df_past = df_original[(df_original["Order Date"] >= past_start_date) & (df_original["Order Date"] <= past_end_date)]

# ---- Apply the same filters as df_filtered ----
if selected_region != "All":
    df_past = df_past[df_past["Region"] == selected_region]

if selected_state != "All":
    df_past = df_past[df_past["State"] == selected_state]

if selected_category != "All":
    df_past = df_past[df_past["Category"] == selected_category]

if selected_subcat != "All":
    df_past = df_past[df_past["Sub-Category"] == selected_subcat]

if selected_segment != "All":
    df_past = df_past[df_past["Segment"] == selected_segment]


# ---- Ensure Past Data Exists ----
past_data_available = not df_past.empty

# ---- Compute KPIs for Current and Past Periods ----
total_sales, avg_order_value, total_orders, total_profit, profit_margin, avg_shipment_time = compute_kpis(df_current)

if past_data_available:
    past_sales, past_avg_order_value, past_orders, past_profit, past_profit_margin, past_shipment_time = compute_kpis(df_past)
else:
    past_sales, past_avg_order_value, past_orders, past_profit, past_profit_margin, past_shipment_time = (0, 0, 0, 0, 0, 0)

# ---- Function to Calculate Percentage Change ----
def calc_percentage_change(current, past):
    """Calculate percentage change safely"""
    if past == 0:
        return 0  # If past data is missing or zero, return 0% change
    return ((current - past) / past) * 100

# ---- Calculate Percentage Changes ----
sales_change = calc_percentage_change(total_sales, past_sales)
avg_order_value_change = calc_percentage_change(avg_order_value, past_avg_order_value)
orders_change = calc_percentage_change(total_orders, past_orders)
profit_change = calc_percentage_change(total_profit, past_profit)
profit_margin_change = calc_percentage_change(profit_margin, past_profit_margin)
shipment_time_change = calc_percentage_change(avg_shipment_time, past_shipment_time)

# ---- Formatting Function for Colored Percentage Change ----
def format_change(value):
    """Format percentage change with colors and symbols"""
    if value == 0:
        return "<span style='color:gray; font-weight:bold;'>➖ 0.0%</span>"  # Neutral gray for no change
    
    color = "green" if value > 0 else "red"
    symbol = "▲" if value > 0 else "▼"
    return f"<span style='color:{color}; font-weight:bold;'> {symbol} {abs(value):.1f}%</span>"

# ---- Display KPI Metrics ----
kpi_cols = st.columns(6, gap="small")

kpi_data = [
    {"title": "Total Sales Revenue", "value": f"${format_number(total_sales)}", "change": sales_change},
    {"title": "Average Order Value", "value": f"${format_number(avg_order_value)}", "change": avg_order_value_change},
    {"title": "Total Orders Placed", "value": f"{format_number(total_orders)}", "change": orders_change},
    {"title": "Total Profit", "value": f"${format_number(total_profit)}", "change": profit_change},
    {"title": "Profit Margin (%)", "value": f"{profit_margin:.1f}%", "change": profit_margin_change},
    {"title": "Average Shipment Time", "value": f"{avg_shipment_time:.1f} Days", "change": shipment_time_change}
]

for i, kpi in enumerate(kpi_data):
    with kpi_cols[i]:
        st.markdown(
            f"""
            <div class='kpi-box'>
                <div class='kpi-title'>{kpi['title']}</div>
                <div class='kpi-value'>{kpi['value']}</div>
                <div class='kpi-change'>{format_change(kpi['change'])}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---- Show Warning If No Past Data Exists ----
if not past_data_available:
    st.warning("No change detected in KPI values compared to the past period, or no past data available, resulting in a 0.0% change.")


# ---- Visualization Section ----
st.markdown("### Trends and Market Insights")

# KPI Selection for visualizations
selected_kpi = st.radio(
    "Select KPI to Display",
    ["Sales", "Profit", "Quantity", "Margin Rate"],
    horizontal=True
)

# Create three equal-width columns
col1, col2, col3 = st.columns([1, 1, 1])

# ---- Line Chart: KPI Over Time ----
with col1:
    st.markdown(f"#### {selected_kpi} Over Time")
    use_moving_avg = st.toggle("Apply Moving Average")

    # Aggregate data by month for time-series visualization
    df_time = df_filtered.groupby(pd.Grouper(key="Order Date", freq="M"))[[selected_kpi]].sum().reset_index()

    if use_moving_avg:
        df_time["Moving Avg"] = df_time[selected_kpi].rolling(window=3).mean()

    # Create line chart
    fig_line = px.line(
        df_time, 
        x="Order Date", 
        y=selected_kpi, 
        labels={selected_kpi: f"{selected_kpi} ($)", "Order Date": "Date"},
        markers=True
    )

    # Add moving average line if selected
    if use_moving_avg:
        fig_line.add_scatter(
            x=df_time["Order Date"], 
            y=df_time["Moving Avg"], 
            mode="lines", 
            name=f"{selected_kpi} (3-Month Avg)", 
            line=dict(dash="dash")
        )

    # Standardize chart height & layout
    fig_line.update_layout(
        height=600,  # **Ensure uniform height**
        margin=dict(l=20, r=20, t=40, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_line, use_container_width=True)

# ---- Bar Chart: Top 10 Products ----
with col2:
    st.markdown(f"#### Top 10 Products by {selected_kpi}")

    # Group by Product Name and aggregate the selected KPI
    df_product_sales = df_filtered.groupby("Product Name")[[selected_kpi]].sum().reset_index()
    df_top10 = df_product_sales.sort_values(by=selected_kpi, ascending=False).head(10)

    # Create horizontal bar chart
    fig_top10 = px.bar(
        df_top10, 
        x=selected_kpi, 
        y="Product Name", 
        orientation="h",
        labels={selected_kpi: f"Total {selected_kpi} ($)", "Product Name": "Product"},
        color=selected_kpi,
        color_continuous_scale="Blues"
    )

    # Keep highest value on top and maintain uniform size
    fig_top10.update_layout(
        height=600,  # **Ensure uniform height**
        margin=dict(l=20, r=20, t=40, b=40),
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_top10, use_container_width=True)

# ---- Map Chart: KPI by Geography ----
with col3:
    st.markdown(f"#### {selected_kpi} by Region")

    # Aggregate state-level data
    df_geo = df_filtered.groupby("State")[[selected_kpi]].sum().reset_index()

    # Load US state abbreviations for mapping
    state_abbr = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv")[["state", "code"]]
    df_geo = df_geo.merge(state_abbr, left_on="State", right_on="state", how="left")

    # Create choropleth map
    fig_map = px.choropleth(
        df_geo, 
        locations="code", 
        locationmode="USA-states", 
        color=selected_kpi,
        color_continuous_scale="Blues", 
        scope="usa",
        labels={selected_kpi: f"Total {selected_kpi} ($)"},
    )

    # **Ensure uniform size and layout**
    fig_map.update_layout(
        height=600,  # **Ensure uniform height**
        margin=dict(l=20, r=20, t=40, b=40),
        coloraxis_colorbar=dict(
            title=f"Total {selected_kpi} ($)",
            thicknessmode="pixels", thickness=15,  # Thicker color scale
            lenmode="fraction", len=0.7,  # Extend color scale height
            yanchor="middle", y=0.5,
            xanchor="left", x=1.02
        )
    )

    # **Display the larger map**
    st.plotly_chart(fig_map, use_container_width=True)
