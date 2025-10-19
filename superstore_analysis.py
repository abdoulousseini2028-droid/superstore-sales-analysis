"""
Superstore Sales Performance Analysis
=====================================
Business intelligence project analyzing retail sales data to identify revenue 
opportunities, optimize product mix, and understand customer behavior patterns.

Dataset: 9,994 retail transactions with sales, profit, and customer demographics
Analysis Focus: Regional performance, product profitability, customer segmentation
Author: Abdoul Rahim Ousseini
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Load retail transaction data
df = pd.read_csv('Sample - Superstore.csv', encoding='latin-1')

# Prepare date columns for time-series analysis
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Extract time periods for trend analysis
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Year-Month'] = df['Order Date'].dt.strftime('%Y-%m')

print(f"Dataset loaded: {len(df):,} transactions")
print(f"Date range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")

# Load data into SQL database for complex aggregations
conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index=False, if_exists='replace')

print("\n" + "="*70)
print("BUSINESS METRICS ANALYSIS")
print("="*70)

# Analysis 1: Regional revenue performance
# Identifies which geographic markets generate highest revenue and profit
query_regional = """
SELECT 
    Region,
    ROUND(SUM(Sales), 2) as Total_Revenue,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(AVG(Profit / Sales * 100), 2) as Profit_Margin_Pct,
    COUNT(DISTINCT "Customer ID") as Num_Customers
FROM sales
GROUP BY Region
ORDER BY Total_Revenue DESC
"""
revenue_by_region = pd.read_sql_query(query_regional, conn)
print("\n1. REGIONAL PERFORMANCE")
print(revenue_by_region.to_string(index=False))

# Analysis 2: Product profitability ranking
# Determines which specific products drive the most profit
query_products = """
SELECT 
    "Product Name",
    Category,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    COUNT(*) as Units_Sold
FROM sales
GROUP BY "Product Name", Category
ORDER BY Total_Profit DESC
LIMIT 10
"""
top_products = pd.read_sql_query(query_products, conn)
print("\n2. TOP 10 PROFIT-GENERATING PRODUCTS")
print(top_products.to_string(index=False))

# Analysis 3: Category-level performance comparison
# Evaluates which product lines have best margins and revenue potential
query_category = """
SELECT 
    Category,
    ROUND(SUM(Sales), 2) as Total_Revenue,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(AVG(Profit / Sales * 100), 2) as Profit_Margin_Pct
FROM sales
GROUP BY Category
ORDER BY Total_Revenue DESC
"""
category_performance = pd.read_sql_query(query_category, conn)
print("\n3. PRODUCT CATEGORY BREAKDOWN")
print(category_performance.to_string(index=False))

# Analysis 4: Customer segment value analysis
# Compares business value across consumer types for targeted marketing
query_segments = """
SELECT 
    Segment,
    COUNT(DISTINCT "Customer ID") as Num_Customers,
    ROUND(SUM(Sales), 2) as Total_Revenue,
    ROUND(AVG(Sales), 2) as Avg_Order_Value,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM sales
GROUP BY Segment
ORDER BY Total_Revenue DESC
"""
segment_analysis = pd.read_sql_query(query_segments, conn)
print("\n4. CUSTOMER SEGMENT ANALYSIS")
print(segment_analysis.to_string(index=False))

# Analysis 5: Time-series trend for forecasting
# Tracks monthly revenue patterns to identify seasonality
query_monthly = """
SELECT 
    "Year-Month",
    ROUND(SUM(Sales), 2) as Monthly_Revenue,
    ROUND(SUM(Profit), 2) as Monthly_Profit
FROM sales
GROUP BY "Year-Month"
ORDER BY "Year-Month"
"""
monthly_trend = pd.read_sql_query(query_monthly, conn)

conn.close()

# Calculate executive summary metrics
total_revenue = df['Sales'].sum()
total_profit = df['Profit'].sum()
avg_profit_margin = (total_profit / total_revenue) * 100
best_region = revenue_by_region.iloc[0]['Region']
best_category = category_performance.iloc[0]['Category']

print("\n" + "="*70)
print("EXECUTIVE SUMMARY")
print("="*70)
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Overall Profit Margin: {avg_profit_margin:.1f}%")
print(f"Top Performing Region: {best_region} (${revenue_by_region.iloc[0]['Total_Revenue']:,.2f})")
print(f"Most Profitable Category: {best_category} (${category_performance.iloc[0]['Total_Profit']:,.2f})")

# Generate data visualizations for stakeholder reporting
print("\n" + "="*70)
print("CREATING VISUALIZATIONS")
print("="*70)

# Visualization 1: Regional revenue comparison
plt.figure(figsize=(10, 6))
colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
bars = plt.bar(revenue_by_region['Region'], revenue_by_region['Total_Revenue'], 
               color=colors, edgecolor='black', linewidth=1.2)
plt.title('Revenue Performance by Geographic Region', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Region', fontsize=12)
plt.ylabel('Total Revenue ($)', fontsize=12)
plt.ticklabel_format(style='plain', axis='y')

# Add revenue labels on bars for clarity
for i, (region, revenue) in enumerate(zip(revenue_by_region['Region'], revenue_by_region['Total_Revenue'])):
    plt.text(i, revenue + 10000, f'${revenue:,.0f}', ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('revenue_by_region.png', dpi=150, bbox_inches='tight')
print("Saved: revenue_by_region.png")
plt.show()

# Visualization 2: Profit margin efficiency by category
plt.figure(figsize=(10, 6))
bars = plt.barh(category_performance['Category'], category_performance['Profit_Margin_Pct'], 
                color='steelblue', edgecolor='black', linewidth=1.2)
plt.title('Profit Margin Comparison Across Product Categories', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Profit Margin (%)', fontsize=12)
plt.ylabel('Product Category', fontsize=12)

# Display margin percentages
for i, (cat, margin) in enumerate(zip(category_performance['Category'], category_performance['Profit_Margin_Pct'])):
    plt.text(margin + 0.3, i, f'{margin:.1f}%', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('profit_margin_category.png', dpi=150, bbox_inches='tight')
print("Saved: profit_margin_category.png")
plt.show()

# Visualization 3: Customer segment revenue distribution
plt.figure(figsize=(8, 8))
colors_pie = ['#3498db', '#e74c3c', '#2ecc71']
wedges, texts, autotexts = plt.pie(segment_analysis['Total_Revenue'], 
                                     labels=segment_analysis['Segment'], 
                                     autopct='%1.1f%%',
                                     startangle=90, 
                                     colors=colors_pie,
                                     textprops={'fontsize': 12, 'fontweight': 'bold'})
plt.title('Revenue Split by Customer Segment', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('revenue_by_segment.png', dpi=150, bbox_inches='tight')
print("Saved: revenue_by_segment.png")
plt.show()

# Visualization 4: Monthly revenue trend analysis
plt.figure(figsize=(12, 6))
plt.plot(range(len(monthly_trend)), monthly_trend['Monthly_Revenue'], 
         marker='o', linewidth=2.5, color='#2ecc71', markersize=6, markerfacecolor='white', 
         markeredgewidth=2, markeredgecolor='#2ecc71')
plt.title('Monthly Revenue Trend Over Time', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Time Period', fontsize=12)
plt.ylabel('Monthly Revenue ($)', fontsize=12)
plt.xticks(range(0, len(monthly_trend), 3), monthly_trend['Year-Month'][::3], rotation=45, ha='right')
plt.grid(True, alpha=0.3, linestyle='--')
plt.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.savefig('monthly_revenue_trend.png', dpi=150, bbox_inches='tight')
print("Saved: monthly_revenue_trend.png")
plt.show()

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("Generated 4 visualizations and important business metrics")
print("Charts saved - Ready for stakeholder presentation")
