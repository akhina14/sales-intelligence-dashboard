import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.markdown("""
<style>
.stApp {background-color: #F8FAFC;}

[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);}

div[data-testid="stPlotlyChart"] {
    background-color: white;
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);}

[data-testid="stSidebar"] {
    background-color: #EEF2FF;}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
padding:20px;
border-radius:15px;
background: linear-gradient(90deg,#2563EB,#4F46E5);
color:white;
">
<h1>📊 Sales Intelligence Dashboard</h1>
<p>
Revenue Analytics • Forecasting • Anomaly Detection • Business Insights
</p>
</div>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "📈 Sales Trends",
    "📦 Product Analysis",
    "⚠ Anomalies",
    "🏆 Profitability",
    "💡 Business Insights"])

# Load data
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

data_path = os.path.join(BASE_DIR, "data", "processed", "superstore_features.csv")
forecast_path = os.path.join(BASE_DIR, "data", "processed", "sales_forecast.csv")

df = pd.read_csv(data_path, encoding="latin1")
forecast_df = pd.read_csv(forecast_path, encoding="latin1")

df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Ship Date"] = pd.to_datetime(df["Ship Date"])
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])

filtered_df = df.copy()



#Filters
st.sidebar.title("⚙ Dashboard Controls")
st.sidebar.markdown("---")

st.sidebar.markdown("### Filter Data")
st.sidebar.info(
"""
Use filters to analyze
sales performance by
region and category.
""")
region = st.sidebar.selectbox("Select Region",["All"] + list(df["Region"].unique()))
category = st.sidebar.selectbox("Select Category",["All"] + list(df["Category"].unique()))

if region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == region]

if category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == category]
loss_df = filtered_df[filtered_df["Profit"] < 0]

# KPIs
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()

daily_sales = filtered_df.groupby("Order Date")["Sales"].sum().reset_index()
monthly = (filtered_df.set_index("Order Date").sort_index().resample("ME")["Sales"].sum().reset_index())
cat_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
profit_cat = filtered_df.groupby("Category")["Profit"].sum().reset_index()
avg_discount = filtered_df["Discount"].mean()
avg_margin = filtered_df["Profit Margin"].mean()

with tab1:

    st.markdown("## 📊 Executive Overview")
    forecast_total = forecast_df["Forecast Sales"].sum()

   
    c1, c2, c3 = st.columns(3)

    c1.metric("💰 Revenue", f"${total_sales:,.0f}")
    c2.metric("🛒 Orders", total_orders)
    c3.metric("🔮 Total Profit",f"${total_profit:,.0f}")
    st.divider()

    left, right = st.columns([2, 1])

    #  LEFT SIDE 
    with left:
         #  COMBINED OPERATIONS BOX 
            
        st.markdown("### 📦 Operations Overview")
        st.success(f"🎯 Average Discount: {avg_discount:.1%}")
        st.info(f"🧾 Unique Products: {filtered_df['Product Name'].nunique()}")
        st.warning(f"🚀 Average Profit Margin: {avg_margin:.1%}")
  
         # TOP DRIVERS 
        st.markdown("### 🏆 Top Revenue Drivers")
        top_cat = (filtered_df.groupby("Category")["Sales"].sum().sort_values(ascending=False).head(3))
        for i, (cat, val) in enumerate(top_cat.items(), 1):
            st.write(f"**{i}. {cat}** → ${val:,.0f}")

    #  RIGHT SIDE 
    with right:
        st.markdown("### 🧠 Business Health")
        profit_margin = filtered_df["Profit Margin"].mean()
        if profit_margin > 0.2:
            st.success("🟢 Strong Profitability")
        elif profit_margin > 0.1:
            st.warning("🟡 Moderate Profitability")
        else:
            st.error("🔴 Low Profitability")

        st.markdown("### ⚠ Risk Snapshot")
        loss_orders = filtered_df[filtered_df["Profit"] < 0].shape[0]
        high_discount = filtered_df[filtered_df["Discount"] > 0.3].shape[0]

        st.metric("Loss Orders", loss_orders)
        st.metric("High Discount Orders", high_discount)

        

with tab2:
    last_actual = monthly["Sales"].iloc[-1]
    projected_revenue = forecast_df["Forecast Sales"].iloc[-1]
    diff = ((projected_revenue - last_actual) / last_actual) * 100

    st.info(f"""🚀 Forecast Outlook Projected

    Next period: ${projected_revenue:,.0f}
    Last actual period: ${last_actual:,.0f}
    Change: {diff:.2f}%
    """)
    
    left, right = st.columns(2)

    with left:
        
        fig = px.line(monthly,x="Order Date",y="Sales",markers=True,title="📈 Monthly Revenue Trend")
        fig.update_layout(hovermode="x unified",xaxis_title="Month-Year",yaxis_title="Sales ($)")
        fig.update_xaxes(tickformat="%b %Y")
        st.plotly_chart(fig, use_container_width=True)
        forecast_total = forecast_df["Forecast Sales"].sum()


    with right:
        st.plotly_chart(px.line(forecast_df,x="Date",y="Forecast Sales",title="🔮 Sales Forecast"),
            use_container_width=True)
        
    weekday_sales = (filtered_df.groupby("Order DayOfWeek")["Sales"].sum().reset_index())
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday_sales["Order DayOfWeek"] = pd.Categorical(weekday_sales["Order DayOfWeek"],
    categories=day_order,ordered=True)

    weekday_sales = weekday_sales.sort_values("Order DayOfWeek")
    fig_weekday = px.bar(weekday_sales,x="Order DayOfWeek",y="Sales",title="📅 Sales by Day of Week")
    fig_weekday.update_layout(xaxis_title="Day of Week",yaxis_title="Sales ($)")
    st.plotly_chart(fig_weekday,use_container_width=True)


import plotly.graph_objects as go

combined_df = (filtered_df.groupby("Category")[["Sales", "Profit"]].sum().reset_index())

fig = go.Figure()

fig.add_bar(x=combined_df["Category"],y=combined_df["Sales"],name="Sales")

fig.add_scatter(x=combined_df["Category"],y=combined_df["Profit"],mode="lines+markers",
    name="Profit",yaxis="y2")

fig.update_layout(yaxis=dict(title="Sales"),
    yaxis2=dict(
        title="Profit",overlaying="y",side="right",showgrid=False),legend=dict(orientation="h"))


with tab3:
    left, right = st.columns([3,2])

    with left:
      st.subheader("📦 Sales & Profit by Category")
      fig.update_layout(margin=dict(l=80, r=180, t=60, b=80),legend=dict(orientation="h", y=1.15))
      st.plotly_chart(fig, use_container_width=True)

    with right:
      st.subheader("🌍 Region Share")
      pie_fig = px.pie(region_sales,names="Region",values="Sales")
      pie_fig.update_layout(margin=dict(l=40, r=40, t=50, b=50),legend=dict(orientation="h", y=1.1))
      st.plotly_chart(pie_fig, use_container_width=True)

    top_products = (filtered_df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
    .head(10).reset_index())
    left, right = st.columns(2)

    with left:
        st.subheader("🏆 Top 10 Products")
        st.dataframe(top_products, height=350)

    with right:
        st.subheader("⚠ Loss-Making Orders")
        st.dataframe(loss_df, height=350)

def detect_anomalies(df):
    df = df.copy()
    mean = df["Sales"].mean()
    std = df["Sales"].std()
    df["Z_Score"] = (df["Sales"] - mean) / std
    anomalies = df[(df["Z_Score"] > 2) | (df["Z_Score"] < -2)]
    return anomalies
anomalies_df = detect_anomalies(monthly)

def explain_anomalies(monthly_df, anomalies_df):
    explanations = []

    mean = monthly_df["Sales"].mean()
    std = monthly_df["Sales"].std()

    for _, row in anomalies_df.iterrows():
        value = row["Sales"]
        date = row["Order Date"]

        deviation = ((value - mean) / mean) * 100 if mean != 0 else 0

        if value > mean:
            reason = "spike in demand or bulk orders"
            direction = "above"
        else:
            reason = "unexpected drop in sales activity or seasonality effect"
            direction = "below"

        explanations.append({"date": date,"value": value,"message": (
                f"📅 {date.strftime('%b %Y')}: Sales were {abs(deviation):.1f}% {direction} average, "
                f"suggesting a possible {reason}.")})

    return explanations
anomaly_explanations = explain_anomalies(monthly, anomalies_df)

with tab4:

    st.header("⚠ Anomaly Detection")

   
    # Monthly Sales Anomalies
    

    st.subheader("📈 Monthly Sales Anomalies")

    if anomalies_df.empty:

        st.success("No monthly anomalies detected 🎯")

    else:

        st.warning(f"{len(anomalies_df)} anomalous months detected")

        fig = px.line(monthly, x="Order Date",y="Sales",markers=True,
            title="Monthly Sales Trend with Anomalies")

        fig.add_scatter(x=anomalies_df["Order Date"],y=anomalies_df["Sales"],mode="markers",
            marker=dict(color="red",size=12),name="Anomalies")
        fig.update_xaxes(tickformat="%b %Y")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig,use_container_width=True)

        # AI Insights

        st.subheader("🧠 Monthly Insights")
        for item in anomaly_explanations:
            st.info(item["message"])
    st.divider()

  
# Order-Level Outliers


    st.subheader("🚨 High-Impact Transactions")

    order_outliers = filtered_df[filtered_df["Sales_Outlier"] == 1]


# KPI Summary Row

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("High-Impact Orders", len(order_outliers))

    with c2:
        st.metric("Revenue from Impact Orders",f"${order_outliers['Sales'].sum():,.0f}")

    with c3:
        avg_sales = order_outliers["Sales"].mean() if not order_outliers.empty else 0
        st.metric("Avg Order Value",f"${avg_sales:,.0f}")


# Insight Box

    st.info(
        f"""
    📊 **Insight**

    We identified **{len(order_outliers)} high-impact transactions** that significantly deviate from normal sales behavior.

    💰 These transactions contributed **${order_outliers['Sales'].sum():,.0f}** in revenue.

    📌 Such orders typically represent:
    - Bulk corporate purchases  
    - Seasonal demand spikes  
    - Heavy discount-driven sales
    """)


# Table Section

    if order_outliers.empty:

        st.success("No high-impact transactions detected 🎯")

    else:

        st.markdown("### 📋 Transaction Details")

        st.dataframe(order_outliers[
            ["Order Date","Customer Name","Product Name","Category","Sales","Profit"]].sort_values("Sales", ascending=False),
        use_container_width=True)
with tab5:

    st.header("📊 Profitability Analysis")

    # KPI Section
   

    avg_margin = filtered_df["Profit Margin"].mean()
    total_profit = filtered_df["Profit"].sum()
    avg_discount = filtered_df["Discount"].mean()


    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        margin_df = (filtered_df.groupby("Category")["Profit Margin"]
            .mean().reset_index().sort_values("Profit Margin",ascending=False))
        fig_margin = px.bar(margin_df,x="Category",y="Profit Margin",color="Category",
            title="Average Profit Margin by Category")
        fig_margin.update_layout(showlegend=False)
        st.plotly_chart(fig_margin,use_container_width=True)

    with col2:
        discount_df = (filtered_df.groupby("Category")["Discount Impact"]
            .sum().reset_index().sort_values("Discount Impact",ascending=False))

        fig_discount = px.bar(discount_df,x="Category",y="Discount Impact",color="Category",title="Discount Impact by Category")

        fig_discount.update_layout(showlegend=False)

        st.plotly_chart(fig_discount,use_container_width=True)

    st.divider()

    fig_scatter = px.scatter(filtered_df,x="Discount",y="Profit",color="Category",
        hover_data=["Product Name","Sales"],
        title="Discount vs Profit")

    st.plotly_chart(fig_scatter,use_container_width=True)

  
    # Insights Section
   

    st.divider()

    st.subheader("💡 Profitability Insights")

    best_margin_category = (margin_df.sort_values("Profit Margin",ascending=False)
        .iloc[0]["Category"])

    highest_discount_category = (discount_df.sort_values("Discount Impact",ascending=False)
        .iloc[0]["Category"])

    st.info(
        f"""
        • Highest average profit margin: **{best_margin_category}**

        • Highest discount impact: **{highest_discount_category}**

        • Use the Discount vs Profit chart to identify whether larger discounts are reducing profitability.
        """
    )
def generate_insights(df):
    insights = []
    
    # 1. Top category
    top_category = df.groupby("Category")["Sales"].sum().idxmax()
    insights.append(f"📦 Highest revenue category: {top_category}")

    # 2. Profit margin insight
    margin_by_category = (df.groupby("Category")["Profit Margin"].mean())
    low_margin_category = margin_by_category.idxmin()
    low_margin_value = margin_by_category.min()
    insights.append(f"📉 Lowest profit margin category: {low_margin_category} ({low_margin_value:.1%})")
    
    # 3. Top region
    top_region = df.groupby("Region")["Sales"].sum().idxmax()
    insights.append(f"🌍 Best performing region: {top_region}")

    # 4. Loss warning
    loss = df[df["Profit"] < 0]["Sales"].sum()
    if loss > 0:
        insights.append(f"⚠ Loss-making sales detected worth ${loss:,.0f}")

    # 5. Trend insight
    if len(monthly) > 1:
       change = ((monthly["Sales"].iloc[-1] - monthly["Sales"].iloc[-2])/ monthly["Sales"].iloc[-2]) * 100

    if change > 0:
        insights.append(f"📈 Sales increased by {change:.2f}% last month")
    else:
        insights.append(f"📉 Sales dropped by {abs(change):.2f}% last month")

    return insights


insights = generate_insights(filtered_df)

with tab6:

    st.markdown("---")
    st.markdown(
    "<h1 style='font-size:34px;'>💡Business Insights</h1>",
    unsafe_allow_html=True)

    # Executive Summary Card
    st.markdown(
        f"""
        <div style="
            background:white;
            padding:20px;
            border-radius:12px;
            box-shadow:0px 2px 8px rgba(0,0,0,0.08);
        ">
            <h4>Executive Summary</h4>
            <p><b>💰 Total Sales:</b> ${total_sales:,.0f}</p>
            <p><b>📈 Total Profit:</b> ${total_profit:,.0f}</p>
            <p><b>🏷 Average Discount:</b> {avg_discount * 100:.2f}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Automated Insights")

    
    for ins in insights:
        st.markdown(
            f"""
            <div style="
                background:white;
                padding:12px;
                border-radius:10px;
                margin-bottom:8px;
                box-shadow:0px 1px 4px rgba(0,0,0,0.05);
                border-left:4px solid #4F46E5;
            ">
                {ins}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### Recommendations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Focus on high-revenue categories")

    with col2:
        st.warning("Improve low-margin segments")

    with col3:
        st.success("Optimize discount strategy")