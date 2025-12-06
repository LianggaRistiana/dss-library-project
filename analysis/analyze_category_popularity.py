import pandas as pd
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

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

def analyze_category_popularity():
    details, items, masters, categories = load_data()
    if details is None:
        return

    print("Processing data for Category Popularity...")

    # Prepare DataFrames with clean column names
    details_df = details[['borrowId', 'bookItemId']].copy()
    
    items_df = items[['id', 'masterId']].copy()
    items_df.columns = ['bookItemId', 'masterId']
    
    masters_df = masters[['id', 'categoryId']].copy()
    masters_df.columns = ['masterId', 'categoryId']
    
    categories_df = categories[['id', 'name']].copy()
    categories_df.columns = ['categoryId', 'category_name']

    # Merge
    merged = details_df.merge(items_df, on='bookItemId', how='left')
    merged = merged.merge(masters_df, on='masterId', how='left')
    merged = merged.merge(categories_df, on='categoryId', how='left')
    
    # Category Popularity
    print("Analyzing category popularity...")
    category_counts = merged['category_name'].value_counts().reset_index()
    category_counts.columns = ['category', 'borrow_count']
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    popularity_path = os.path.join(OUTPUT_DIR, "category_popularity.csv")
    category_counts.to_csv(popularity_path, index=False)
    print(f"Category popularity saved to {popularity_path}")

if __name__ == "__main__":
    analyze_category_popularity()
