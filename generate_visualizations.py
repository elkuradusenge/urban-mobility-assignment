"""
Generate visualizations from analysis results
Creates charts and graphs for the technical report
"""
import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("=" * 70)
print("GENERATING VISUALIZATIONS")
print("=" * 70)

# Create output directory
viz_dir = 'analysis_results/visualizations'
if not os.path.exists(viz_dir):
    os.makedirs(viz_dir)

# Load analysis results
print("\nLoading analysis results...")
with open('analysis_results/temporal_analysis.json', 'r') as f:
    temporal = json.load(f)
with open('analysis_results/spatial_analysis.json', 'r') as f:
    spatial = json.load(f)
with open('analysis_results/economic_analysis.json', 'r') as f:
    economic = json.load(f)
with open('analysis_results/operational_analysis.json', 'r') as f:
    operational = json.load(f)

# 1. Hourly Trip Distribution
print("Creating: Hourly Trip Distribution...")
plt.figure(figsize=(14, 6))
hours = sorted(temporal['hourly_distribution']['data'].keys(), key=int)
counts = [temporal['hourly_distribution']['data'][h] for h in hours]
plt.bar(hours, counts, color='steelblue', edgecolor='navy', alpha=0.7)
plt.xlabel('Hour of Day', fontsize=12, fontweight='bold')
plt.ylabel('Number of Trips', fontsize=12, fontweight='bold')
plt.title('NYC Taxi Trips by Hour of Day', fontsize=14, fontweight='bold')
plt.xticks(hours)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{viz_dir}/hourly_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Period Distribution
print("Creating: Period Distribution...")
plt.figure(figsize=(10, 6))
periods = list(temporal['period_distribution']['data'].keys())
counts = list(temporal['period_distribution']['data'].values())
colors = ['#FF6B6B', '#FFE66D', '#4ECDC4', '#45B7D1']
plt.bar(periods, counts, color=colors, edgecolor='black', alpha=0.8)
plt.xlabel('Time Period', fontsize=12, fontweight='bold')
plt.ylabel('Number of Trips', fontsize=12, fontweight='bold')
plt.title('NYC Taxi Trips by Time Period', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
for i, v in enumerate(counts):
    plt.text(i, v + 20000, f'{v:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/period_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Borough Distribution
print("Creating: Borough Distribution...")
plt.figure(figsize=(12, 6))
boroughs = list(spatial['pickup_boroughs']['distribution'].keys())
counts = list(spatial['pickup_boroughs']['distribution'].values())
# Sort by count
sorted_data = sorted(zip(boroughs, counts), key=lambda x: x[1], reverse=True)
boroughs_sorted = [x[0] for x in sorted_data]
counts_sorted = [x[1] for x in sorted_data]
plt.barh(boroughs_sorted, counts_sorted, color='coral', edgecolor='darkred', alpha=0.7)
plt.xlabel('Number of Pickups', fontsize=12, fontweight='bold')
plt.ylabel('Borough', fontsize=12, fontweight='bold')
plt.title('NYC Taxi Pickups by Borough', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)
for i, v in enumerate(counts_sorted):
    percentage = (v / sum(counts_sorted)) * 100
    plt.text(v + 50000, i, f'{v:,} ({percentage:.1f}%)', va='center', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/borough_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Top Pickup Zones
print("Creating: Top Pickup Zones...")
plt.figure(figsize=(14, 8))
top_zones = list(spatial['pickup_zones']['top_20'].keys())[:15]
top_counts = list(spatial['pickup_zones']['top_20'].values())[:15]
plt.barh(range(len(top_zones)), top_counts, color='mediumseagreen', edgecolor='darkgreen', alpha=0.7)
plt.yticks(range(len(top_zones)), top_zones)
plt.xlabel('Number of Pickups', fontsize=12, fontweight='bold')
plt.ylabel('Zone', fontsize=12, fontweight='bold')
plt.title('Top 15 Pickup Zones in NYC', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(f'{viz_dir}/top_pickup_zones.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Payment Type Distribution
print("Creating: Payment Type Distribution...")
plt.figure(figsize=(10, 6))
payment_types = list(economic['payment_type_distribution'].keys())
payment_counts = [economic['payment_type_distribution'][pt]['count'] for pt in payment_types]
colors_payment = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
plt.pie(payment_counts, labels=payment_types, autopct='%1.1f%%', 
        startangle=90, colors=colors_payment, textprops={'fontsize': 11, 'fontweight': 'bold'})
plt.title('Payment Method Distribution', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/payment_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 6. Fare Distribution Box Plot
print("Creating: Fare Distribution...")
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
percentiles = economic['average_values']
avg_fare = percentiles['average_fare']
avg_tip = percentiles['average_tip']
avg_total = percentiles['average_total']
categories = ['Fare', 'Tip', 'Total']
averages = [avg_fare, avg_tip, avg_total]
colors_bar = ['#3498db', '#2ecc71', '#e74c3c']
bars = plt.bar(categories, averages, color=colors_bar, edgecolor='black', alpha=0.7, width=0.6)
plt.ylabel('Average Amount ($)', fontsize=12, fontweight='bold')
plt.title('Average Fare, Tip, and Total Amount', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'${height:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
plt.tight_layout()
plt.savefig(f'{viz_dir}/fare_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 7. Speed Distribution
print("Creating: Speed Distribution...")
plt.figure(figsize=(10, 6))
speed_percentiles = operational['speed_metrics']['percentiles']
percentile_labels = list(speed_percentiles.keys())
speed_values = list(speed_percentiles.values())
plt.plot(percentile_labels, speed_values, marker='o', color='purple', linewidth=2, markersize=10)
plt.xlabel('Percentile', fontsize=12, fontweight='bold')
plt.ylabel('Speed (mph)', fontsize=12, fontweight='bold')
plt.title('Trip Speed Distribution by Percentile', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
for i, v in enumerate(speed_values):
    plt.text(i, v + 0.5, f'{v:.2f}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/speed_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 8. Passenger Count Distribution
print("Creating: Passenger Distribution...")
plt.figure(figsize=(10, 6))
passenger_dist = operational['passenger_metrics']['distribution']
# Get top 6
top_passengers = sorted(passenger_dist.items(), key=lambda x: x[1]['count'], reverse=True)[:6]
labels = [x[0] for x in top_passengers]
counts = [x[1]['count'] for x in top_passengers]
plt.bar(range(len(labels)), counts, color='teal', edgecolor='darkslategray', alpha=0.7)
plt.xticks(range(len(labels)), labels, rotation=15)
plt.xlabel('Number of Passengers', fontsize=12, fontweight='bold')
plt.ylabel('Number of Trips', fontsize=12, fontweight='bold')
plt.title('Trip Distribution by Passenger Count', fontsize=14, fontweight='bold')
plt.grid(axis='y', alpha=0.3)
for i, v in enumerate(counts):
    plt.text(i, v + 50000, f'{v:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/passenger_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# 9. Revenue by Hour
print("Creating: Revenue by Hour...")
plt.figure(figsize=(14, 6))
hours = sorted(temporal['hourly_revenue']['data'].keys(), key=int)
revenue = [temporal['hourly_revenue']['data'][h] for h in hours]
plt.plot(hours, revenue, marker='o', color='green', linewidth=2, markersize=8)
plt.fill_between(hours, revenue, alpha=0.3, color='lightgreen')
plt.xlabel('Hour of Day', fontsize=12, fontweight='bold')
plt.ylabel('Total Revenue ($)', fontsize=12, fontweight='bold')
plt.title('Total Revenue by Hour of Day', fontsize=14, fontweight='bold')
plt.xticks(hours)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{viz_dir}/hourly_revenue.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "=" * 70)
print("✓ All visualizations generated successfully!")
print(f"✓ Saved to: {viz_dir}/")
print("=" * 70)
