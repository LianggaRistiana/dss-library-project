import pandas as pd
import os

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_FILE = "dss_recommendations.csv"

# Weights for DSS Score
WEIGHT_BORROW_COUNT = 1.0
WEIGHT_POOR_COPY = 10.0  # High priority to replace poor copies
WEIGHT_FAIR_COPY = 2.0   # Medium priority
WEIGHT_LOST_COPY = 15.0  # Highest priority (if we had lost status, keeping for future)

def load_data():
    print("Loading data...")
    try:
        items = pd.read_csv(os.path.join(DATASET_DIR, "book_items.csv"))
        masters = pd.read_csv(os.path.join(DATASET_DIR, "book_masters.csv"))
        
        # We can use the existing book_analysis.csv for borrow counts if available, 
        # but recalculating ensures we are self-contained or we can use top_books.csv
        # Let's use top_books.csv if it exists, otherwise recalculate or load borrow_details
        top_books_path = os.path.join(OUTPUT_DIR, "top_books.csv")
        if os.path.exists(top_books_path):
            popularity = pd.read_csv(top_books_path)
        else:
            print("top_books.csv not found, please run analyze_top_books.py first.")
            return None, None, None
            
        return items, masters, popularity
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None

def calculate_dss_score(row):
    score = (row['borrow_count'] * WEIGHT_BORROW_COUNT) + \
            (row['poor_copies'] * WEIGHT_POOR_COPY) + \
            (row['fair_copies'] * WEIGHT_FAIR_COPY)
    return score

def determine_action(row):
    actions = []
    if row['poor_copies'] > 0:
        actions.append(f"Replace {row['poor_copies']} Poor cop{'y' if row['poor_copies']==1 else 'ies'}")
    
    if row['borrow_count'] > 10: # Arbitrary threshold for "High Demand"
        actions.append("Buy more copies (High Demand)")
    elif row['borrow_count'] > 5 and row['total_copies'] < 3:
        actions.append("Buy more copies (Low Stock)")
        
    if not actions:
        return "No Action Needed"
    
    return ", ".join(actions)

def run_dss():
    items, masters, popularity = load_data()
    if items is None:
        return

    print("Running DSS Analysis...")

    # 1. Analyze Inventory Condition per Master Book
    # Create dummies for condition
    condition_dummies = pd.get_dummies(items['condition'])
    items_with_condition = pd.concat([items, condition_dummies], axis=1)
    
    # Ensure columns exist (in case no 'Poor' items exist in dataset)
    for col in ['Poor', 'Fair', 'Good', 'New']:
        if col not in items_with_condition.columns:
            items_with_condition[col] = 0
            
    # Group by masterId
    inventory_status = items_with_condition.groupby('masterId').agg({
        'id': 'count',
        'Poor': 'sum',
        'Fair': 'sum',
        'Good': 'sum',
        'New': 'sum'
    }).reset_index()
    
    inventory_status.rename(columns={'id': 'total_copies', 'Poor': 'poor_copies', 'Fair': 'fair_copies'}, inplace=True)
    
    # 2. Merge with Popularity (Borrow Counts)
    # popularity has masterId, title, author, borrow_count
    dss_df = popularity.merge(inventory_status, on='masterId', how='left')
    
    # Fill NaN for books that might be in popularity list but have no items (unlikely but possible if items deleted)
    # Or books in inventory that have 0 borrows (won't be in top_books if it only lists borrowed ones? 
    # analyze_top_books uses left join from details, so it lists borrowed books. 
    # We should probably do a right join if we want to evaluate ALL books, but for "Repurchase", 
    # we usually care about active ones or broken ones. 
    # Let's stick to books that have activity OR have poor copies.
    # Actually, if a book is never borrowed, we probably don't need to replace its poor copy immediately.
    
    dss_df['total_copies'] = dss_df['total_copies'].fillna(0)
    dss_df['poor_copies'] = dss_df['poor_copies'].fillna(0)
    dss_df['fair_copies'] = dss_df['fair_copies'].fillna(0)
    
    # 3. Calculate Score
    dss_df['recommendation_score'] = dss_df.apply(calculate_dss_score, axis=1)
    
    # 4. Determine Action
    dss_df['recommended_action'] = dss_df.apply(determine_action, axis=1)
    
    # 5. Filter and Sort
    # We only care about items with Score > 0 or specific actions
    recommendations = dss_df[dss_df['recommendation_score'] > 0].sort_values(by='recommendation_score', ascending=False)
    
    # Select output columns
    output_cols = ['masterId', 'title', 'author', 'borrow_count', 'total_copies', 'poor_copies', 'fair_copies', 'recommendation_score', 'recommended_action']
    final_output = recommendations[output_cols]
    
    # Save
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    final_output.to_csv(output_path, index=False)
    print(f"DSS Recommendations saved to {output_path}")
    
    print("\nTop 10 Recommendations:")
    print(final_output.head(10))

if __name__ == "__main__":
    run_dss()
