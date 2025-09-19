import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ✅ Page config must come first
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ----------------------
# Load Data
# ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_dashboard_dataset.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    # Add demo countries (replace with real country column if you have one)
    countries = ["United States", "India", "Germany", "Brazil", "Australia", "Canada", "United Kingdom"]
    df["Country"] = [random.choice(countries) for _ in range(len(df))]
    return df

df = load_data()

st.title("📊 Interactive Sales Dashboard")

# ----------------------
# Sidebar Filters
# ----------------------
st.sidebar.header("Filters")

# Date filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min(), df["Date"].max()]
)

# Region filter
region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Category filter
category_filter = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Customer filter
customer_filter = st.sidebar.multiselect(
    "Select Customer",
    options=df["Customer"].unique(),
    default=df["Customer"].unique()
)

# Theme toggle
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

# ----------------------
# Apply Filters
# ----------------------
# Convert date inputs to pandas Timestamps
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[-1])

df_filtered = df[
    (df["Date"].between(start_date, end_date)) &
    (df["Region"].isin(region_filter)) &
    (df["Category"].isin(category_filter)) &
    (df["Customer"].isin(customer_filter))
]

# Global Search
search_term = st.text_input("🔍 Search by Product or Customer")
if search_term:
    df_filtered = df_filtered[
        df_filtered["Product"].str.contains(search_term, case=False) |
        df_filtered["Customer"].str.contains(search_term, case=False)
    ]

# ----------------------
# KPI Section
# ----------------------
total_sales = df_filtered["TotalSales"].sum()
total_quantity = df_filtered["Quantity"].sum()
avg_order_value = df_filtered["TotalSales"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📦 Total Quantity", f"{total_quantity:,}")
col3.metric("📊 Avg. Order Value", f"${avg_order_value:,.2f}")

st.markdown("---")

# ----------------------
# Charts
# ----------------------
if not df_filtered.empty:
    # Sales over time
    fig_sales_time = px.line(
        df_filtered.groupby("Date")["TotalSales"].sum().reset_index(),
        x="Date", y="TotalSales", title="Sales Over Time",
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_sales_time, use_container_width=True)

    # Monthly Sales Trend
    monthly = df_filtered.groupby(df_filtered["Date"].dt.to_period("M"))["TotalSales"].sum().reset_index()
    monthly["Date"] = monthly["Date"].astype(str)
    fig_monthly = px.bar(
        monthly, x="Date", y="TotalSales",
        title="Monthly Sales Trend",
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Sales by Region
    fig_region = px.bar(
        df_filtered.groupby("Region")["TotalSales"].sum().reset_index(),
        x="Region", y="TotalSales", title="Sales by Region",
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_region, use_container_width=True)

    # Sales by Category
    fig_category = px.pie(
        df_filtered.groupby("Category")["TotalSales"].sum().reset_index(),
        values="TotalSales", names="Category", title="Sales by Category",
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_category, use_container_width=True)

    # Top Products
    top_products = df_filtered.groupby("Product")["TotalSales"].sum().nlargest(10).reset_index()
    fig_products = px.bar(
        top_products, x="Product", y="TotalSales",
        title="Top 10 Products", text_auto=True,
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_products, use_container_width=True)

    # Top Customers
    top_customers = df_filtered.groupby("Customer")["TotalSales"].sum().nlargest(10).reset_index()
    fig_customers = px.bar(
        top_customers, x="Customer", y="TotalSales",
        title="Top 10 Customers", text_auto=True,
        template="plotly_dark" if theme == "Dark" else "plotly_white"
    )
    st.plotly_chart(fig_customers, use_container_width=True)

    # 🌍 World Sales Map
    sales_by_country = df_filtered.groupby("Country")["TotalSales"].sum().reset_index()
    fig_map = px.choropleth(
        sales_by_country,
        locations="Country",
        locationmode="country names",
        color="TotalSales",
        hover_name="Country",
        title="🌍 Sales by Country",
        template="plotly_dark" if theme == "Dark" else "plotly_white",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ----------------------
# Summary Tables
# ----------------------
st.subheader("📊 Sales Summary by Region and Category")
col4, col5 = st.columns(2)

with col4:
    st.write("**By Region**")
    st.dataframe(df_filtered.groupby("Region")["TotalSales"].sum().reset_index())

with col5:
    st.write("**By Category**")
    st.dataframe(df_filtered.groupby("Category")["TotalSales"].sum().reset_index())

st.markdown("---")

# ----------------------
# Data Table
# ----------------------
st.subheader("📑 Sales Data (Editable & Sortable)")
st.data_editor(df_filtered, use_container_width=True)

# Download option
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_download = convert_df(df_filtered)
st.download_button(
    "📥 Download Filtered Data as CSV",
    data=csv_download,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)
