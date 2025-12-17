import pandas as pd
import os
import itertools
from collections import Counter

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_FILE = "category_association.csv"

# Minimum Support Threshold (e.g., 0.01%)
MIN_SUPPORT = 0.0001

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

    # Merge: Borrow Details -> Items -> Masters -> Categories
    merged = details_df.merge(items_df, on='bookItemId', how='left')
    merged = merged.merge(masters_df, on='masterId', how='left')
    merged = merged.merge(categories_df, on='categoryId', how='left')
    
    # Group by Transaction to get list of unique categories per transaction
    transactions_cats = merged.groupby('borrowId')['category_name'].apply(lambda x: sorted(list(set(x))))
    
    # Filter transactions with at least 1 category
    transactions_cats = transactions_cats[transactions_cats.apply(len) >= 1]
    
    total_transactions = len(transactions_cats)
    print(f"Total transactions for analysis: {total_transactions}")
    
    if total_transactions == 0:
        print("Not enough data for category association.")
        return

    # --- Phase 1: 1-Itemset Generation (Frequent Categories) ---
    print("\n[Phase 1] Top 1-Itemsets (Single Categories)")
    
    c1_counts = Counter()
    for cats in transactions_cats:
        for cat in cats:
            c1_counts[cat] += 1
            
    l1_frequent = {}
    for cat, count in c1_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l1_frequent[cat] = support
            
    print(f"Found {len(l1_frequent)} frequent categories (Min Support: {MIN_SUPPORT})")
    
    frequent_cats_list = sorted(list(l1_frequent.keys()))

    # --- Phase 2: 2-Itemset Generation (Frequent Category Pairs) ---
    print("\n[Phase 2] Top 2-Itemsets (Category Pairs)")
    
    c2_counts = Counter()
    
    for cats in transactions_cats:
        frequent_cats_in_tx = [c for c in cats if c in l1_frequent]
        for pair in itertools.combinations(sorted(frequent_cats_in_tx), 2):
            c2_counts[pair] += 1
            
    l2_frequent = {}
    l2_counts_filtered = {}
    
    for pair, count in c2_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l2_frequent[pair] = support
            l2_counts_filtered[pair] = count
            
    print(f"Found {len(l2_frequent)} frequent category pairs (Min Support: {MIN_SUPPORT})")

    # --- Phase 3: 3-Itemset Generation (Frequent Category Triplets) ---
    print("\n[Phase 3] Top 3-Itemsets (Category Triplets)")
    
    c3_counts = Counter()
    
    for cats in transactions_cats:
        frequent_cats_in_tx = [c for c in cats if c in l1_frequent]
        if len(frequent_cats_in_tx) < 3:
            continue
            
        for triplet in itertools.combinations(sorted(frequent_cats_in_tx), 3):
             c3_counts[triplet] += 1

    l3_frequent = {}
    l3_counts_filtered = {}
    
    for triplet, count in c3_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l3_frequent[triplet] = support
            l3_counts_filtered[triplet] = count
            
    print(f"Found {len(l3_frequent)} frequent category triplets (Min Support: {MIN_SUPPORT})")

    # --- Save Frequent Itemsets to CSV ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    itemset_rows = []

    # L1
    for item, support in l1_frequent.items():
        itemset_rows.append({
            'Itemset': item,
            'Itemset_Size': 1,
            'Count': int(support * total_transactions),
            'Support': round(support, 4)
        })

    # L2
    for pair, support in l2_frequent.items():
        itemset_rows.append({
            'Itemset': ' | '.join(pair),
            'Itemset_Size': 2,
            'Count': l2_counts_filtered[pair],
            'Support': round(support, 4)
        })

    # L3
    for triplet, support in l3_frequent.items():
        itemset_rows.append({
            'Itemset': ' | '.join(triplet),
            'Itemset_Size': 3,
            'Count': l3_counts_filtered[triplet],
            'Support': round(support, 4)
        })

    itemsets_df = pd.DataFrame(itemset_rows)
    itemsets_df = itemsets_df.sort_values(by=['Itemset_Size', 'Support'], ascending=[True, False])
    
    itemset_output_path = os.path.join(OUTPUT_DIR, "frequent_category_itemsets.csv")
    itemsets_df.to_csv(itemset_output_path, index=False)
    print(f"Frequent category itemsets saved to {itemset_output_path}")

    # --- Phase 4: Association Rule Generation ---
    print("\n[Phase 4] Generating Association Rules")
    
    results = []
    
    # Rules from L2
    for pair, support_ab in l2_frequent.items():
        cat_a, cat_b = pair
        count = l2_counts_filtered[pair]
        
        support_a = l1_frequent[cat_a]
        support_b = l1_frequent[cat_b]
        
        # A -> B
        confidence = support_ab / support_a
        lift = support_ab / (support_a * support_b)
        results.append({
            'Antecedent': cat_a,
            'Consequent': cat_b,
            'Support': round(support_ab, 4),
            'Confidence': round(confidence, 4),
            'Lift': round(lift, 4),
            'Count': count
        })
        
        # B -> A
        confidence = support_ab / support_b
        results.append({
            'Antecedent': cat_b,
            'Consequent': cat_a,
            'Support': round(support_ab, 4),
            'Confidence': round(confidence, 4),
            'Lift': round(lift, 4),
            'Count': count
        })
        
    # Rules from L3
    for triplet, support_abc in l3_frequent.items():
        count = l3_counts_filtered[triplet]
        
        for consequent in triplet:
            antecedent_tuple = tuple(sorted(x for x in triplet if x != consequent))
            support_antecedent = l2_frequent.get(antecedent_tuple)
            support_consequent = l1_frequent[consequent]
            
            if support_antecedent:
                confidence = support_abc / support_antecedent
                lift = support_abc / (support_antecedent * support_consequent)
                
                results.append({
                    'Antecedent': ' | '.join(antecedent_tuple),
                    'Consequent': consequent,
                    'Support': round(support_abc, 4),
                    'Confidence': round(confidence, 4),
                    'Lift': round(lift, 4),
                    'Count': count
                })
        
    results_df = pd.DataFrame(results)
    
    if not results_df.empty:
        results_df = results_df.sort_values(by=['Lift', 'Confidence'], ascending=[False, False])
        
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        results_df.to_csv(output_path, index=False)
        print(f"Category association analysis saved to {output_path}")
        
        print("\nTop 10 Category Associations:")
        print(results_df.head(10))
    else:
        print("No category associations found meeting the criteria.")

if __name__ == "__main__":
    analyze_category_association()
