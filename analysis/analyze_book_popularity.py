import pandas as pd
import os
import datetime

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_FILE = "book_analysis.csv"
CURRENT_YEAR = datetime.datetime.now().year
NEW_BOOK_THRESHOLD_YEARS = 3 # Books published in the last 3 years are "New"

def load_data():
    print("Loading data...")
    try:
        books = pd.read_csv(os.path.join(DATASET_DIR, "book_masters.csv"))
        items = pd.read_csv(os.path.join(DATASET_DIR, "book_items.csv"))
        borrows = pd.read_csv(os.path.join(DATASET_DIR, "borrow_details.csv"))
        return books, items, borrows
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def analyze_books():
    books, items, borrows = load_data()
    if books is None:
        return

    print("Processing data...")

    # 1. Count borrows per Book Master
    # Join borrows -> items -> masters
    # borrows has 'bookItemId'
    # items has 'id' and 'masterId'
    
    # Merge borrows with items to get masterId
    borrow_counts = borrows.merge(items[['id', 'masterId']], left_on='bookItemId', right_on='id', how='left')
    
    # Group by masterId and count
    borrow_counts_per_master = borrow_counts.groupby('masterId').size().reset_index(name='borrow_count')
    
    # Merge back to books
    books_analysis = books.merge(borrow_counts_per_master, left_on='id', right_on='masterId', how='left')
    
    # Fill NaN borrow counts with 0
    books_analysis['borrow_count'] = books_analysis['borrow_count'].fillna(0)
    
    # 2. Determine "New" vs "Old"
    # New if year >= CURRENT_YEAR - NEW_BOOK_THRESHOLD_YEARS + 1
    # e.g. 2025, threshold 3 -> 2025, 2024, 2023 are New.
    threshold_year = CURRENT_YEAR - NEW_BOOK_THRESHOLD_YEARS + 1
    books_analysis['is_new'] = books_analysis['year'] >= threshold_year
    
    # 3. Determine Demand (Laku Keras vs Tidak Laku)
    # We'll use quantiles for dynamic categorization
    # But first, let's see if we can define "Laku Keras" and "Tidak Laku"
    # If borrow_count is 0, it's definitely "Tidak Laku" (Low Demand)
    
    # Let's use percentiles for the non-zero borrows to find "High Demand"
    # Or simply split into 3 tiers: Low (Bottom 33%), Average (Mid 33%), High (Top 33%)
    
    # Calculate quantiles
    q33 = books_analysis['borrow_count'].quantile(0.33)
    q66 = books_analysis['borrow_count'].quantile(0.66)
    
    print(f"Borrow Count Thresholds: Low < {q33:.2f}, High > {q66:.2f}")

    def categorize(row):
        is_new = row['is_new']
        count = row['borrow_count']
        
        # Determine Demand
        if count <= q33:
            demand = "Low"
        elif count > q66:
            demand = "High"
        else:
            demand = "Average"
            
        # Assign Category
        if demand == "Average":
            return "AVERAGE"
        
        if is_new:
            if demand == "High":
                return "HOT"
            else: # Low
                return "FLOP"
        else: # Old
            if demand == "High":
                return "EVERGREEN"
            else: # Low
                return "DEAD STOCK"

    books_analysis['category'] = books_analysis.apply(categorize, axis=1)
    
    # Select columns for output
    output_df = books_analysis[['id', 'title', 'author', 'year', 'borrow_count', 'category']]
    
    # Save to CSV
    output_path = os.path.join(SCRIPT_DIR, "output", OUTPUT_FILE)
    output_df.to_csv(output_path, index=False)
    print(f"Analysis saved to {output_path}")
    
    # Print summary
    print("\nCategory Distribution:")
    print(output_df['category'].value_counts())

if __name__ == "__main__":
    analyze_books()
