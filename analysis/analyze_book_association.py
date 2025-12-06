import pandas as pd
import os
import itertools
from collections import Counter

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "../dataset")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
OUTPUT_FILE = "association_analysis.csv"

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
    transactions, details, items, masters = load_data()
    if transactions is None:
        return

    print("Processing data...")

    # 1. Merge data to get Transaction -> Book Title
    # details links transaction (borrowId) to item (bookItemId)
    # items links item (id) to master (masterId)
    # masters links master (id) to title
    
    # Merge details with items
    merged_items = details.merge(items[['id', 'masterId']], left_on='bookItemId', right_on='id', how='left')
    
    # Merge with masters to get titles
    merged_masters = merged_items.merge(masters[['id', 'title']], left_on='masterId', right_on='id', how='left')
    
    # We need 'borrowId' and 'title'
    # Drop rows where title is missing (if any)
    df = merged_masters[['borrowId', 'title']].dropna()
    
    # 2. Group by Transaction to get list of books
    # Remove duplicate titles in the same transaction (if a user borrowed 2 copies of the same book, it counts as 1 for association)
    transactions_books = df.groupby('borrowId')['title'].apply(lambda x: sorted(list(set(x))))
    
    # Filter transactions with at least 2 books
    transactions_books = transactions_books[transactions_books.apply(len) >= 2]
    
    print(f"Found {len(transactions_books)} transactions with 2+ books.")
    
    if len(transactions_books) == 0:
        print("Not enough data for association analysis.")
        return

    # 3. Count Frequencies
    book_counts = Counter()
    pair_counts = Counter()
    total_transactions = len(transactions_books) # Or should it be total valid transactions? 
    # Usually total transactions in the dataset is used for support. 
    # Let's use the count of transactions that have at least 1 book involved in the analysis scope, 
    # but strictly speaking, support = count(A&B) / N. 
    # Let's use N = number of transactions with >= 2 items for "conditional" probability context, 
    # or better, use the total number of transactions in the filtered set.
    
    for books in transactions_books:
        # Count individual books
        for book in books:
            book_counts[book] += 1
        
        # Count pairs
        # Generate all combinations of 2
        for pair in itertools.combinations(books, 2):
            pair_counts[pair] += 1
            
    # 4. Calculate Metrics
    results = []
    
    print("Calculating metrics...")
    
    for pair, count in pair_counts.items():
        book_a, book_b = pair
        
        support_a = book_counts[book_a] / total_transactions
        support_b = book_counts[book_b] / total_transactions
        support_ab = count / total_transactions
        
        confidence_a_to_b = support_ab / support_a
        confidence_b_to_a = support_ab / support_b
        
        lift = support_ab / (support_a * support_b)
        
        # Add A -> B
        results.append({
            'Antecedent': book_a,
            'Consequent': book_b,
            'Support': round(support_ab, 4),
            'Confidence': round(confidence_a_to_b, 4),
            'Lift': round(lift, 4),
            'Count': count
        })
        
        # Add B -> A (Symmetric for Support and Lift, different for Confidence)
        results.append({
            'Antecedent': book_b,
            'Consequent': book_a,
            'Support': round(support_ab, 4),
            'Confidence': round(confidence_b_to_a, 4),
            'Lift': round(lift, 4),
            'Count': count
        })
        
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by Lift desc, then Confidence desc
    if not results_df.empty:
        results_df = results_df.sort_values(by=['Lift', 'Confidence'], ascending=[False, False])
        
        # Save to CSV
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        results_df.to_csv(output_path, index=False)
        print(f"Association analysis saved to {output_path}")
        
        # Preview
        print("\nTop 10 Associations:")
        print(results_df.head(10))
    else:
        print("No associations found.")

if __name__ == "__main__":
    analyze_association()
