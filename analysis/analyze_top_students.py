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

def analyze_top_students():
    print("Starting Top Student Borrowers Analysis...")
    
    # Load data
    transactions_path = os.path.join(DATA_DIR, "borrow_transactions.csv")
    students_path = os.path.join(DATA_DIR, "students.csv")
    
    if not os.path.exists(transactions_path) or not os.path.exists(students_path):
        print(f"Error: Required files not found.")
        return

    df_trans = pd.read_csv(transactions_path)
    df_students = pd.read_csv(students_path)
    
    # Count borrowings per student
    student_counts = df_trans['studentId'].value_counts().reset_index()
    student_counts.columns = ['studentId', 'borrow_count']
    
    # Merge with student details to get names
    # Note: Using 'id' from students.csv and 'studentId' from borrow_transactions.csv
    df_merged = pd.merge(student_counts, df_students, left_on='studentId', right_on='id', how='left')
    
    # Get top 10 students
    top_10_students = df_merged.head(10)
    
    print("\nTop 10 Students by Borrowing Count:")
    print(top_10_students[['name', 'studentId', 'borrow_count']])
    
    # Visualization using Seaborn and Matplotlib
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_10_students, x='borrow_count', y='name', hue='name', palette='viridis', legend=False)
    
    plt.title('Top 10 Students with Most Borrowings', fontsize=16)
    plt.xlabel('Number of Borrowings', fontsize=12)
    plt.ylabel('Student Name', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    output_path = os.path.join(VIS_DIR, 'top_student_borrowers.png')
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    analyze_top_students()
