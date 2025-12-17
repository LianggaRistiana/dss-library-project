import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
VIS_DIR = os.path.join(SCRIPT_DIR, "visualizations")

def load_data():
    print("Loading data...")
    try:
        details = pd.read_csv(os.path.join(DATASET_DIR, "borrow_details.csv"))
        items = pd.read_csv(os.path.join(DATASET_DIR, "book_items.csv"))
        masters = pd.read_csv(os.path.join(DATASET_DIR, "book_masters.csv"))
        categories = pd.read_csv(os.path.join(DATASET_DIR, "categorys.csv"))
        return details, items, masters, categories
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None, None

def analyze_clustering():
    details, items, masters, categories = load_data()
    if details is None:
        return

    print("Preprocessing data for Clustering...")

    # 1. Feature Engineering: Borrow Frequency
    # Merge details -> items -> masters to get borrow count per masterId
    merged = details.merge(items[['id', 'masterId']], left_on='bookItemId', right_on='id', how='left')
    
    # Count borrows per book master
    borrow_counts = merged.groupby('masterId').size().reset_index(name='BorrowCount')
    
    # Merge with Masters to get other features (Year, Category)
    book_features = masters.merge(borrow_counts, left_on='id', right_on='masterId', how='left')
    
    # Fill NaN BorrowCount with 0 (books never borrowed)
    book_features['BorrowCount'] = book_features['BorrowCount'].fillna(0)
    
    # Merge Category Name
    # Rename category columns to avoid collision with book 'id'
    categories_renamed = categories[['id', 'name']].rename(columns={'id': 'cat_id', 'name': 'CategoryName'})
    book_features = book_features.merge(categories_renamed, left_on='categoryId', right_on='cat_id', how='left')
    
    # Select relevant columns for clustering
    # Features: BorrowCount, Year, Category (One-Hot)
    # Filter valid years (e.g. > 1900 to avoid outliers if any)
    
    # For visualization and ID purposes
    df_model = book_features[['id', 'title', 'year', 'CategoryName', 'BorrowCount']].copy()
    
    # Drop rows with missing values if any
    df_model = df_model.dropna()

    print(f"Data shape for clustering: {df_model.shape}")
    
    # 2. Data Preparation for K-Means
    # One-Hot Encode Category
    df_encoded = pd.get_dummies(df_model, columns=['CategoryName'], drop_first=False)
    
    # Select numeric columns for scaling
    # We include encoded columns + Year + BorrowCount
    # Exclude ID and Title
    features_to_scale = [col for col in df_encoded.columns if col not in ['id', 'title']]
    
    X = df_encoded[features_to_scale]
    
    # Scale Features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 3. K-Means Clustering
    k = 4 # Number of clusters (can be tuned)
    print(f"Running K-Means with k={k}...")
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Add Cluster back to original DF
    df_model['Cluster'] = clusters
    
    # 4. Analysis of Clusters
    print("\nCluster Profiling:")
    cluster_profile = df_model.groupby('Cluster').agg({
        'BorrowCount': ['mean', 'min', 'max'],
        'year': ['mean', 'min', 'max'],
        'id': 'count'
    }).round(2)
    print(cluster_profile)
    
    # Save Results
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_path = os.path.join(OUTPUT_DIR, "book_clustering.csv")
    df_model.to_csv(output_path, index=False)
    print(f"Clustering results saved to {output_path}")
    
    # 5. Visualizations
    if not os.path.exists(VIS_DIR):
        os.makedirs(VIS_DIR)
        
    # Set style
    sns.set(style="whitegrid")
    
    # Visualization A: Scatter Plot (Year vs Borrow Count)
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=df_model,
        x='year',
        y='BorrowCount',
        hue='Cluster',
        palette='viridis',
        style='Cluster',
        s=100,
        alpha=0.8
    )
    plt.title('Book Clustering: Publication Year vs Borrow Frequency', fontsize=16)
    plt.xlabel('Publication Year', fontsize=12)
    plt.ylabel('Borrow Frequency', fontsize=12)
    plt.legend(title='Cluster')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "book_clustering_scatter.png"))
    plt.close()
    
    # Visualization B: Box Plot (Borrow Count Distribution by Cluster)
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Cluster', y='BorrowCount', data=df_model, palette='viridis')
    plt.title('Borrow Frequency Distribution by Cluster', fontsize=16)
    plt.xlabel('Cluster ID')
    plt.ylabel('Borrow Count')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "book_clustering_boxplot.png"))
    plt.close()
    
    print("Visualizations saved.")

if __name__ == "__main__":
    analyze_clustering()
