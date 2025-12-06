import pandas as pd
import os
import itertools
from collections import Counter

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

def analyze_category_association():
    details, items, masters, categories = load_data()
    if details is None:
        return

    print("Processing data for Category Association...")

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
    
    # Category Association
    print("Analyzing category associations...")
    
    # Group by borrowId
    transactions_cats = merged.groupby('borrowId')['category_name'].apply(lambda x: sorted(list(set(x))))
    
    # Filter for transactions with >= 2 categories
    transactions_cats = transactions_cats[transactions_cats.apply(len) >= 2]
    
    print(f"Found {len(transactions_cats)} transactions with 2+ distinct categories.")
    
    if len(transactions_cats) > 0:
        cat_counts = Counter()
        pair_counts = Counter()
        total_transactions = len(transactions_cats)
        
        for cats in transactions_cats:
            for cat in cats:
                cat_counts[cat] += 1
            
            for pair in itertools.combinations(cats, 2):
                pair_counts[pair] += 1
        
        results = []
        for pair, count in pair_counts.items():
            cat_a, cat_b = pair
            
            support_a = cat_counts[cat_a] / total_transactions
            support_b = cat_counts[cat_b] / total_transactions
            support_ab = count / total_transactions
            
            confidence_a_to_b = support_ab / support_a
            confidence_b_to_a = support_ab / support_b
            
            lift = support_ab / (support_a * support_b)
            
            results.append({
                'Antecedent': cat_a,
                'Consequent': cat_b,
                'Support': round(support_ab, 4),
                'Confidence': round(confidence_a_to_b, 4),
                'Lift': round(lift, 4),
                'Count': count
            })
            results.append({
                'Antecedent': cat_b,
                'Consequent': cat_a,
                'Support': round(support_ab, 4),
                'Confidence': round(confidence_b_to_a, 4),
                'Lift': round(lift, 4),
                'Count': count
            })
            
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values(by=['Lift', 'Confidence'], ascending=[False, False])
            
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
                
            assoc_path = os.path.join(OUTPUT_DIR, "category_association.csv")
            results_df.to_csv(assoc_path, index=False)
            print(f"Category association saved to {assoc_path}")
        else:
            print("No category associations found.")
    else:
        print("Not enough data for category association.")

if __name__ == "__main__":
    analyze_category_association()
