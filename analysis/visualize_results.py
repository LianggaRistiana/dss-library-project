import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import networkx as nx

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
VIS_DIR = os.path.join(SCRIPT_DIR, "visualizations")

if not os.path.exists(VIS_DIR):
    os.makedirs(VIS_DIR)

def load_data():
    book_analysis_path = os.path.join(OUTPUT_DIR, "book_analysis.csv")
    association_analysis_path = os.path.join(OUTPUT_DIR, "association_analysis.csv")
    category_popularity_path = os.path.join(OUTPUT_DIR, "category_popularity.csv")
    category_association_path = os.path.join(OUTPUT_DIR, "category_association.csv")
    top_books_path = os.path.join(OUTPUT_DIR, "top_books.csv")
    dss_path = os.path.join(OUTPUT_DIR, "dss_recommendations.csv")
    
    books_df = None
    assoc_df = None
    cat_pop_df = None
    cat_assoc_df = None
    top_books_df = None
    dss_df = None
    
    if os.path.exists(book_analysis_path):
        books_df = pd.read_csv(book_analysis_path)
    
    if os.path.exists(association_analysis_path):
        assoc_df = pd.read_csv(association_analysis_path)
        
    if os.path.exists(category_popularity_path):
        cat_pop_df = pd.read_csv(category_popularity_path)
        
    if os.path.exists(category_association_path):
        cat_assoc_df = pd.read_csv(category_association_path)
        
    if os.path.exists(top_books_path):
        top_books_df = pd.read_csv(top_books_path)
        
    if os.path.exists(dss_path):
        dss_df = pd.read_csv(dss_path)
        
    return books_df, assoc_df, cat_pop_df, cat_assoc_df, top_books_df, dss_df

def visualize_books(df):
    if df is None:
        return

    print("Visualizing Book Analysis...")
    
    # 1. Category Distribution (from book analysis)
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='category', order=df['category'].value_counts().index, hue='category', palette='viridis', legend=False)
    plt.title('Distribution of Book Categories (HOT/FLOP/etc)')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.savefig(os.path.join(VIS_DIR, 'book_status_distribution.png'))
    plt.close()
    
    # 2. Borrow Count Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['borrow_count'], bins=20, kde=True)
    plt.title('Distribution of Borrow Counts')
    plt.xlabel('Borrow Count')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(VIS_DIR, 'borrow_count_distribution.png'))
    plt.close()
    
    # 3. Year vs Borrow Count (Scatter)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='year', y='borrow_count', hue='category', alpha=0.6, palette='viridis')
    plt.title('Publication Year vs Borrow Count')
    plt.xlabel('Year')
    plt.ylabel('Borrow Count')
    plt.savefig(os.path.join(VIS_DIR, 'year_vs_borrow_count.png'))
    plt.close()

def visualize_top_books(df):
    if df is None:
        return
        
    print("Visualizing Top Books...")
    
    top_10 = df.head(10)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_10, x='borrow_count', y='title', hue='title', palette='plasma', legend=False)
    plt.title('Top 10 Most Borrowed Books')
    plt.xlabel('Borrow Count')
    plt.ylabel('Book Title')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'top_10_books.png'))
    plt.close()

def visualize_dss(df):
    if df is None:
        return
        
    print("Visualizing DSS Recommendations...")
    
    top_10 = df.head(10)
    
    plt.figure(figsize=(12, 8))
    # Using horizontal bar chart for better readability of titles
    sns.barplot(data=top_10, x='recommendation_score', y='title', hue='title', palette='Reds_r', legend=False)
    plt.title('Top 10 Books Recommended for Repurchase/Restock')
    plt.xlabel('Recommendation Score')
    plt.ylabel('Book Title')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'dss_top_recommendations.png'))
    plt.close()

def visualize_associations(df, filename_prefix="association"):
    if df is None:
        return

    print(f"Visualizing Association Analysis ({filename_prefix})...")
    
    # Filter for top rules by Lift
    top_rules = df.head(20)
    
    # 1. Scatter Plot: Support vs Confidence (colored by Lift)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Support', y='Confidence', hue='Lift', size='Lift', sizes=(20, 200), palette='coolwarm', alpha=0.7)
    plt.title(f'{filename_prefix.capitalize()} Rules: Support vs Confidence')
    plt.xlabel('Support')
    plt.ylabel('Confidence')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, f'{filename_prefix}_scatter.png'))
    plt.close()
    
    # 2. Network Graph of Top Associations
    try:
        G = nx.DiGraph()
        
        # Add edges for top 10 rules to avoid clutter
        top_10 = df.head(10)
        for _, row in top_10.iterrows():
            G.add_edge(row['Antecedent'], row['Consequent'], weight=row['Lift'])
            
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=1.5) # Increased k for better spacing
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightgreen', alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray', arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        # Edge labels (Lift)
        edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        
        plt.title(f'Top 10 {filename_prefix.capitalize()} Rules (Network Graph)')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, f'{filename_prefix}_network.png'))
        plt.close()
    except Exception as e:
        print(f"Error creating network graph for {filename_prefix}: {e}")

def visualize_categories(pop_df):
    if pop_df is None:
        return
        
    print("Visualizing Category Popularity...")
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=pop_df, x='borrow_count', y='category', hue='category', palette='magma', legend=False)
    plt.title('Most Popular Book Categories')
    plt.xlabel('Borrow Count')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'category_popularity.png'))
    plt.close()

def main():
    books_df, assoc_df, cat_pop_df, cat_assoc_df, top_books_df, dss_df = load_data()
    visualize_books(books_df)
    visualize_top_books(top_books_df)
    visualize_dss(dss_df)
    visualize_associations(assoc_df, "book_association")
    visualize_categories(cat_pop_df)
    visualize_associations(cat_assoc_df, "category_association")
    print(f"Visualizations saved to {VIS_DIR}")

if __name__ == "__main__":
    main()
