import pandas as pd
import os
import itertools
from collections import Counter

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_FILE = "association_analysis.csv"

# Minimum Support Threshold (e.g., 0.01%)
MIN_SUPPORT = 0.0001

def load_data():
    print("Loading data...")
    try:
        # Load necessary files
        transactions = pd.read_csv(os.path.join(DATASET_DIR, "borrow_transactions.csv"))
        details = pd.read_csv(os.path.join(DATASET_DIR, "borrow_details.csv"))
        items = pd.read_csv(os.path.join(DATASET_DIR, "book_items.csv"))
        masters = pd.read_csv(os.path.join(DATASET_DIR, "book_masters.csv"))
        return transactions, details, items, masters
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return None, None, None, None

def analyze_association():
    transactions_df, details, items, masters = load_data()
    if transactions_df is None:
        return

    print("Processing data...")

    # Data Preparation: Merge to get Transaction -> Book Title
    merged_items = details.merge(items[['id', 'masterId']], left_on='bookItemId', right_on='id', how='left')
    merged_masters = merged_items.merge(masters[['id', 'title']], left_on='masterId', right_on='id', how='left')
    
    df = merged_masters[['borrowId', 'title']].dropna()
    
    # Group by Transaction to get list of books
    transactions_books = df.groupby('borrowId')['title'].apply(lambda x: sorted(list(set(x))))
    
    # Filter transactions with at least 1 book
    transactions_books = transactions_books[transactions_books.apply(len) >= 1]
    
    total_transactions = len(transactions_books)
    print(f"Total transactions for analysis: {total_transactions}")
    
    if total_transactions == 0:
        print("Not enough data for association analysis.")
        return

    # --- Phase 1: 1-Itemset Generation ---
    print("\n[Phase 1] Top 1-Itemsets (Single Items)")
    
    c1_counts = Counter()
    for books in transactions_books:
        for book in books:
            c1_counts[book] += 1
            
    l1_frequent = {}
    for book, count in c1_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l1_frequent[book] = support
            
    print(f"Found {len(l1_frequent)} frequent 1-itemsets (Min Support: {MIN_SUPPORT})")
    
    frequent_items_list = sorted(list(l1_frequent.keys()))

    # --- Phase 2: 2-Itemset Generation ---
    print("\n[Phase 2] Top 2-Itemsets (Item Pairs)")
    
    c2_counts = Counter()
    
    # Count 2-itemsets
    for books in transactions_books:
        frequent_books_in_tx = [b for b in books if b in l1_frequent]
        for pair in itertools.combinations(sorted(frequent_books_in_tx), 2):
            c2_counts[pair] += 1
            
    l2_frequent = {}
    l2_counts_filtered = {}
    
    for pair, count in c2_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l2_frequent[pair] = support
            l2_counts_filtered[pair] = count
            
    print(f"Found {len(l2_frequent)} frequent 2-itemsets (Min Support: {MIN_SUPPORT})")

    # --- Phase 3: 3-Itemset Generation ---
    print("\n[Phase 3] Top 3-Itemsets (Item Triplets)")
    
    c3_counts = Counter()
    
    # Simple generation: iterate transactions and find triplets of frequent items
    # Optimization: A triplet is candidate only if all its pairs are in L2 (Apriori Property)
    # But for simplicity and speed on small data, we can just checking combos in transactions directly 
    # and strictly filtering by min_support is efficient enough here.
    
    for books in transactions_books:
        # We only care about books that are involved in at least one frequent pair (L2)
        # Or simpler: books that are in L1.
        frequent_books_in_tx = [b for b in books if b in l1_frequent]
        
        # We need at least 3 items to form a triplet
        if len(frequent_books_in_tx) < 3:
            continue
            
        for triplet in itertools.combinations(sorted(frequent_books_in_tx), 3):
            # Optimization check: logic check, are all subsets frequent?
            # subset_pairs = itertools.combinations(triplet, 2)
            # if all(pair in l2_frequent for pair in subset_pairs):
            c3_counts[triplet] += 1

    l3_frequent = {}
    l3_counts_filtered = {}
    
    for triplet, count in c3_counts.items():
        support = count / total_transactions
        if support >= MIN_SUPPORT:
            l3_frequent[triplet] = support
            l3_counts_filtered[triplet] = count
            
    print(f"Found {len(l3_frequent)} frequent 3-itemsets (Min Support: {MIN_SUPPORT})")

    # --- Save Frequent Itemsets to CSV ---
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
    
    itemset_output_path = os.path.join(OUTPUT_DIR, "frequent_itemsets.csv")
    itemsets_df.to_csv(itemset_output_path, index=False)
    print(f"Frequent itemsets saved to {itemset_output_path}")
    
    # --- Generate Association Rules ---
    print("\n[Phase 4] Generating Association Rules")
    
    results = []
    
    # Rules from L2: {A} -> {B}
    for pair, support_ab in l2_frequent.items():
        book_a, book_b = pair
        count = l2_counts_filtered[pair]
        
        support_a = l1_frequent[book_a]
        support_b = l1_frequent[book_b]
        
        # A -> B
        results.append({
            'Antecedent': book_a,
            'Consequent': book_b,
            'Support': round(support_ab, 4),
            'Confidence': round(support_ab / support_a, 4),
            'Lift': round(support_ab / (support_a * support_b), 4),
            'Count': count
        })
        
        # B -> A
        results.append({
            'Antecedent': book_b,
            'Consequent': book_a,
            'Support': round(support_ab, 4),
            'Confidence': round(support_ab / support_b, 4),
            'Lift': round(support_ab / (support_a * support_b), 4),
            'Count': count
        })

    # Rules from L3: {A, B} -> {C}
    for triplet, support_abc in l3_frequent.items():
        count = l3_counts_filtered[triplet]
        
        # For a triplet {A, B, C}, potential rules are:
        # {A, B} -> C
        # {A, C} -> B
        # {B, C} -> A
        
        for consequent in triplet:
            antecedent_tuple = tuple(sorted(x for x in triplet if x != consequent))
            
            # Use L2 support for antecedent
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
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        results_df.to_csv(output_path, index=False)
        print(f"Association analysis saved to {output_path}")
        
        print("\nTop 10 Association Rules:")
        print(results_df.head(10))
    else:
        print("No association rules found meeting the criteria.")

if __name__ == "__main__":
    analyze_association()
