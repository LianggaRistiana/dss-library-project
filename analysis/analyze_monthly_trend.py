import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "dataset")
VIS_DIR = os.path.join(SCRIPT_DIR, "visualizations")

if not os.path.exists(VIS_DIR):
    os.makedirs(VIS_DIR)

def analyze_monthly_trend():
    print("Starting Monthly Borrowing Trend Analysis...")
    
    # Load data
    transactions_path = os.path.join(DATA_DIR, "borrow_transactions.csv")
    if not os.path.exists(transactions_path):
        print(f"Error: File not found at {transactions_path}")
        return

    df = pd.read_csv(transactions_path)
    
    # Convert 'borrowedAt' to datetime
    df['borrowedAt'] = pd.to_datetime(df['borrowedAt'])
    
    # Extract month (YYYY-MM)
    df['month'] = df['borrowedAt'].dt.to_period('M').astype(str)
    
    # Group by month and count
    monthly_counts = df.groupby('month').size().reset_index(name='borrow_count')
    
    # Sort by month
    monthly_counts = monthly_counts.sort_values('month')
    
    print("\nMonthly Borrowing Counts:")
    print(monthly_counts)
    
    # Visualization using Seaborn and Matplotlib
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_counts, x='month', y='borrow_count', marker='o', linewidth=2, sort=False)
    
    plt.title('Monthly Borrowing Trend', fontsize=16)
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Number of Borrowings', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_path = os.path.join(VIS_DIR, 'monthly_borrowing_trend.png')
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    analyze_monthly_trend()
