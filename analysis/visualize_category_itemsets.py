import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "output", "frequent_category_itemsets.csv")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "visualizations")

# Colors
PRIMARY_COLOR = '#8B5CF6' # Violet
SECONDARY_COLOR = '#F59E0B' # Amber
TERTIARY_COLOR = '#EC4899' # Pink

def visualize_category_itemsets():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    # Load data
    df = pd.read_csv(INPUT_FILE)
    
    # Ensure visualizations directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Map Count to Frequency if necessary
    if 'Frequency' not in df.columns and 'Count' in df.columns:
        df['Frequency'] = df['Count']

    # Add Type column for coloring if not exists
    if 'Type' not in df.columns and 'Itemset_Size' in df.columns:
        df['Type'] = df['Itemset_Size'].apply(lambda x: f"{x}-Itemset")

    # 1. Top 15 All Itemsets
    plt.figure(figsize=(12, 8))
    top_itemsets = df.sort_values(by='Frequency', ascending=False)
    
    # Limit to top 15
    top_itemsets = top_itemsets.head(15)
    
    sns.barplot(
        data=top_itemsets,
        y='Itemset',
        x='Frequency',
        hue='Type',
        palette={'1-Itemset': PRIMARY_COLOR, '2-Itemset': SECONDARY_COLOR, '3-Itemset': TERTIARY_COLOR}
    )
    
    plt.title('Top 15 Most Frequent Category Itemsets', fontsize=16)
    plt.xlabel('Frequency', fontsize=12)
    plt.ylabel('Category Itemset', fontsize=12)
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, "top_category_itemsets.png")
    plt.savefig(output_path)
    print(f"Saved visualization to: {output_path}")
    plt.close()

    # 2. Top 10 1-Itemsets (Single Categories)
    df_single = df[df['Itemset_Size'] == 1].head(10)
    if not df_single.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=df_single,
            y='Itemset',
            x='Frequency',
            color=PRIMARY_COLOR
        )
        plt.title('Top 10 Most Frequent Categories (1-Itemsets)', fontsize=14)
        plt.xlabel('Frequency')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "top_1_category_itemsets.png"))
        plt.close()

    # 3. Top 10 2-Itemsets (Category Pairs)
    df_pairs = df[df['Itemset_Size'] == 2].head(10)
    if not df_pairs.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=df_pairs,
            y='Itemset',
            x='Frequency',
            color=SECONDARY_COLOR
        )
        plt.title('Top 10 Most Frequent Category Pairs (2-Itemsets)', fontsize=14)
        plt.xlabel('Frequency')
        plt.ylabel('Category Pair')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "top_2_category_itemsets.png"))
        plt.close()

    # 4. Top 10 3-Itemsets (Category Triplets)
    df_triplets = df[df['Itemset_Size'] == 3].head(10)
    if not df_triplets.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=df_triplets,
            y='Itemset',
            x='Frequency',
            color=TERTIARY_COLOR
        )
        plt.title('Top 10 Most Frequent Category Triplets (3-Itemsets)', fontsize=14)
        plt.xlabel('Frequency')
        plt.ylabel('Category Triplet')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "top_3_category_itemsets.png"))
        plt.close()
        print("Saved visualization for 3-itemsets")

if __name__ == "__main__":
    visualize_category_itemsets()
