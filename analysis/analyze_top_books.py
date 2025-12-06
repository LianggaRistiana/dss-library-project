import pandas as pd
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_FILE = "top_books.csv"

def load_data():
    print("Loading data...")
    try:
        details = pd.read_csv(os.path.join(DATASET_DIR, "borrow_details.csv"))
        items = pd.read_csv(os.path.join(DATASET_DIR, "book_items.csv"))
        masters = pd.read_csv(os.path.join(DATASET_DIR, "book_masters.csv"))
        return details, items, masters
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def analyze_top_books():
    details, items, masters = load_data()
    if details is None:
        return

    print("Processing data for Top Books...")

    # Prepare DataFrames with clean column names
    details_df = details[['borrowId', 'bookItemId']].copy()
    
    items_df = items[['id', 'masterId']].copy()
    items_df.columns = ['bookItemId', 'masterId']
    
    masters_df = masters[['id', 'title', 'author', 'publisher', 'year']].copy()
    masters_df.columns = ['masterId', 'title', 'author', 'publisher', 'year']

    # Merge: Borrow Details -> Items -> Masters
    merged = details_df.merge(items_df, on='bookItemId', how='left')
    merged = merged.merge(masters_df, on='masterId', how='left')
    
    # Count borrows per book title (or masterId to be precise, then include title)
    # Using masterId to group ensures we don't merge different books with same title (unlikely but safer)
    book_counts = merged.groupby(['masterId', 'title', 'author']).size().reset_index(name='borrow_count')
    
    # Sort by borrow_count descending
    top_books = book_counts.sort_values(by='borrow_count', ascending=False)
    
    # Save to CSV
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    top_books.to_csv(output_path, index=False)
    print(f"Top books analysis saved to {output_path}")
    
    print("\nTop 10 Most Borrowed Books:")
    print(top_books.head(10))

if __name__ == "__main__":
    analyze_top_books()
