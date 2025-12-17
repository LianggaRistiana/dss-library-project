import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
VISUALIZATION_DIR = os.path.join(SCRIPT_DIR, "visualizations")
OUTPUT_FILE = "transaction_size_analysis.csv"

def analyze_transaction_size():
    print("Loading data...")
    try:
        details = pd.read_csv(os.path.join(DATASET_DIR, "borrow_details.csv"))
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    print("Analyzing transaction sizes...")
    
    # Group by borrowId to count items per transaction
    transaction_sizes = details.groupby('borrowId').size().reset_index(name='ItemsCount')
    
    # Count how many transactions have X items
    size_distribution = transaction_sizes['ItemsCount'].value_counts().reset_index()
    size_distribution.columns = ['ItemsPerTransaction', 'Frequency']
    size_distribution = size_distribution.sort_values(by='ItemsPerTransaction')
    
    # Calculate Percentage
    total_transactions = size_distribution['Frequency'].sum()
    size_distribution['Percentage'] = (size_distribution['Frequency'] / total_transactions * 100).round(2)
    
    # Save to CSV
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    size_distribution.to_csv(output_path, index=False)
    print(f"Transaction size analysis saved to {output_path}")
    
    print("\nTransaction Size Distribution:")
    print(size_distribution)

    # Visualize
    if not os.path.exists(VISUALIZATION_DIR):
        os.makedirs(VISUALIZATION_DIR)
        
    plt.figure(figsize=(10, 6))
    
    # Bar plot
    ax = sns.barplot(
        data=size_distribution,
        x='ItemsPerTransaction',
        y='Frequency',
        color='#3B82F6' # Blue
    )
    
    # Add labels on top of bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')
        
    plt.title('Distribution of Books per Transaction', fontsize=16)
    plt.xlabel('Number of Books Borrowed', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.tight_layout()
    
    viz_path = os.path.join(VISUALIZATION_DIR, "transaction_size_distribution.png")
    plt.savefig(viz_path)
    print(f"Visualization saved to {viz_path}")
    plt.close()

if __name__ == "__main__":
    analyze_transaction_size()
