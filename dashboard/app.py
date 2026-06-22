

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Sales Intelligence Dashboard",
    layout="wide"
)

st.title("📊 AI-Powered Sales Intelligence Dashboard")

# Load cleaned data
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "processed", "superstore_clean.csv")

df = pd.read_csv(file_path, encoding="latin1")
# KPIs
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["Order ID"].nunique()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"${total_sales:,.0f}")

with col2:
    st.metric("Total Profit", f"${total_profit:,.0f}")

with col3:
    st.metric("Total Orders", total_orders)


import plotly.express as px

df["Order Date"] = pd.to_datetime(df["Order Date"])
daily_sales = df.groupby("Order Date")["Sales"].sum().reset_index()

fig = px.line(daily_sales, x="Order Date", y="Sales",
              title="📈 Daily Sales Trend")

st.plotly_chart(fig, use_container_width=True)


cat_sales = df.groupby("Category")["Sales"].sum().reset_index()

fig = px.bar(cat_sales, x="Category", y="Sales",
             title="📦 Sales by Category")

st.plotly_chart(fig, use_container_width=True)


region_sales = df.groupby("Region")["Sales"].sum().reset_index()

fig = px.pie(region_sales, names="Region", values="Sales",
             title="🌍 Sales by Region")

st.plotly_chart(fig, use_container_width=True)


profit_cat = df.groupby("Category")["Profit"].sum().reset_index()

fig = px.bar(profit_cat, x="Category", y="Profit",
             title="💰 Profit by Category")

st.plotly_chart(fig, use_container_width=True)

loss_df = df[df["Profit"] < 0]

st.subheader("⚠ Loss-Making Orders")
st.dataframe(loss_df)

st.sidebar.header("Filters")

region = st.sidebar.selectbox("Select Region", df["Region"].unique())
category = st.sidebar.selectbox("Select Category", df["Category"].unique())

filtered_df = df[
    (df["Region"] == region) &
    (df["Category"] == category)
]

st.subheader("🧠 Key Insights")

top_category = df.groupby("Category")["Sales"].sum().idxmax()
top_region = df.groupby("Region")["Sales"].sum().idxmax()

st.write(f"📌 Highest sales category: {top_category}")
st.write(f"📌 Best performing region: {top_region}")