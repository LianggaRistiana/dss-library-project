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

def analyze_late_returns():
    print("Starting Late Returns Analysis...")
    
    # Load data
    borrow_path = os.path.join(DATA_DIR, "borrow_transactions.csv")
    return_path = os.path.join(DATA_DIR, "return_transactions.csv")
    students_path = os.path.join(DATA_DIR, "students.csv")
    
    if not os.path.exists(borrow_path) or not os.path.exists(return_path) or not os.path.exists(students_path):
        print(f"Error: Required files not found.")
        return

    df_borrow = pd.read_csv(borrow_path)
    df_return = pd.read_csv(return_path)
    df_students = pd.read_csv(students_path)
    
    # Merge borrow and return transactions
    # borrow_transactions.id linked to return_transactions.borrowId
    df_merged = pd.merge(df_borrow, df_return, left_on='id', right_on='borrowId', how='inner', suffixes=('_borrow', '_return'))
    
    # Convert dates to datetime
    df_merged['dueDate'] = pd.to_datetime(df_merged['dueDate'])
    df_merged['returnedAt'] = pd.to_datetime(df_merged['returnedAt'])
    
    # Identify late returns
    # Late if returnedAt > dueDate
    df_merged['is_late'] = df_merged['returnedAt'] > df_merged['dueDate']
    
    # Filter only late returns
    late_returns = df_merged[df_merged['is_late']]
    
    # Count late returns per student
    late_counts = late_returns['studentId'].value_counts().reset_index()
    late_counts.columns = ['studentId', 'late_count']
    
    # Merge with student details to get names
    df_analysis = pd.merge(late_counts, df_students, left_on='studentId', right_on='id', how='left')
    
    # Get top 10 students with late returns
    top_10_late = df_analysis.head(10)
    
    print("\nTop 10 Students with Late Returns:")
    print(top_10_late[['name', 'studentId', 'late_count']])
    
    # Visualization
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_10_late, x='late_count', y='name', hue='name', palette='magma', legend=False)
    
    plt.title('Top 10 Students with Most Late Returns', fontsize=16)
    plt.xlabel('Number of Late Returns', fontsize=12)
    plt.ylabel('Student Name', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_path = os.path.join(VIS_DIR, 'top_late_returns.png')
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    analyze_late_returns()
