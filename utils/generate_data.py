import csv
import random
import datetime
from datetime import timedelta
import uuid

# Configuration
NUM_BOOKS = 1000
NUM_ITEMS = 3000
NUM_BORROWS = 2000
NUM_RETURNS = 1500 # Must be <= NUM_BORROWS

DATASET_DIR = "../dataset"

# Helper to read existing CSVs
def read_csv(filename):
    data = []
    with open(f"{DATASET_DIR}/{filename}", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# Helper to write CSVs
def write_csv(filename, fieldnames, data):
    with open(f"{DATASET_DIR}/{filename}", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filename} with {len(data)} records.")

# Load existing data
categories = read_csv("categorys.csv")
students = read_csv("students.csv")
category_ids = [c['id'] for c in categories]
student_ids = [s['id'] for s in students]

# Generate BookMaster
print("Generating BookMaster...")
book_masters = []
titles = ["Introduction to", "Advanced", "The Art of", "Fundamentals of", "Mastering", "History of", "Guide to", "Handbook of"]
subjects = ["Python", "Java", "History", "Physics", "Chemistry", "Biology", "Economics", "Philosophy", "Art", "Music", "Calculus", "AI", "Machine Learning"]
publishers = ["Penguin", "O'Reilly", "Pearson", "McGraw-Hill", "Springer", "Wiley", "MIT Press"]

for i in range(NUM_BOOKS):
    book_id = f"BK-{i+1:04d}" # Overwrite existing ID format if needed, or continue. 
    # Actually, the user provided format BK-001 in category, but book master ID format wasn't strictly specified to match category. 
    # Let's use BM-001 for Book Master to avoid confusion with Category ID (BK-xxx in categorys.csv seems to be category ID based on file content, but user interface said Category ID).
    # Wait, looking at categorys.csv: id is BK-001. 
    # User interface: BookMaster has categoryId.
    # Let's use BM-{number} for BookMaster ID.
    
    title = f"{random.choice(titles)} {random.choice(subjects)} {random.randint(1, 10)}"
    author = f"Author {random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
    
    book_masters.append({
        "id": f"BM-{i+1:04d}",
        "title": title,
        "author": author,
        "publisher": random.choice(publishers),
        "year": random.randint(1990, 2024),
        "categoryId": random.choice(category_ids),
        "isbn": f"978-{random.randint(100000000, 999999999)}"
    })

write_csv("book_masters.csv", ["id", "title", "author", "publisher", "year", "categoryId", "isbn"], book_masters)

# Generate BookItem
print("Generating BookItem...")
book_items = []
conditions = ["Good", "Fair", "Poor", "New"]
statuses = ["Available", "Borrowed", "Lost", "Maintenance"]

item_count = 0
for i in range(NUM_ITEMS):
    master = random.choice(book_masters)
    item_id = f"BI-{i+1:05d}"
    
    book_items.append({
        "id": item_id,
        "masterId": master['id'],
        "code": f"INV-{i+1:06d}",
        "condition": random.choice(conditions),
        "status": "Available", # Initial status, will update based on transactions
        "createdAt": (datetime.datetime.now() - timedelta(days=random.randint(100, 1000))).strftime("%Y-%m-%d %H:%M:%S")
    })

write_csv("book_items.csv", ["id", "masterId", "code", "condition", "status", "createdAt"], book_items)

# Generate BorrowTransaction
print("Generating BorrowTransaction...")
borrow_transactions = []
borrow_details = []
admin_ids = [f"ADM-{i:03d}" for i in range(1, 6)]

# We need to track which items are currently borrowed to avoid double borrowing
item_status_map = {item['id']: "Available" for item in book_items}

start_date = datetime.datetime.now() - timedelta(days=365)

for i in range(NUM_BORROWS):
    borrow_id = f"TRX-{i+1:06d}"
    student_id = random.choice(student_ids)
    borrow_date = start_date + timedelta(days=random.randint(0, 360))
    due_date = borrow_date + timedelta(days=7)
    
    # Select 1-3 items to borrow
    num_items_to_borrow = random.randint(1, 3)
    available_items = [item for item in book_items if item_status_map[item['id']] == "Available"]
    
    if not available_items:
        break # No more items to borrow
        
    selected_items = random.sample(available_items, min(len(available_items), num_items_to_borrow))
    
    # Determine if this transaction is "Returned" or "Borrowed" (Active)
    # For simplicity in generation, let's say earlier transactions are likely returned.
    # But we will handle returns in a separate loop to match the user request structure.
    # For now, mark all as Borrowed, then ReturnTransaction will update them.
    
    borrow_transactions.append({
        "id": borrow_id,
        "adminId": random.choice(admin_ids),
        "studentId": student_id,
        "borrowedAt": borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
        "dueDate": due_date.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Borrowed" 
    })
    
    for item in selected_items:
        borrow_details.append({
            "id": str(uuid.uuid4()),
            "borrowId": borrow_id,
            "bookItemId": item['id'],
            "conditionAtBorrow": item['condition']
        })
        item_status_map[item['id']] = "Borrowed"

write_csv("borrow_transactions.csv", ["id", "adminId", "studentId", "borrowedAt", "dueDate", "status"], borrow_transactions)
write_csv("borrow_details.csv", ["id", "borrowId", "bookItemId", "conditionAtBorrow"], borrow_details)

# Generate ReturnTransaction
print("Generating ReturnTransaction...")
return_transactions = []
return_details = []

# Pick a subset of borrow transactions to return
# Sort by date to return older ones first logic or just random? Random is fine but logical consistency is better.
# Let's just pick random subset.
borrows_to_return = random.sample(borrow_transactions, min(len(borrow_transactions), NUM_RETURNS))

for i, borrow in enumerate(borrows_to_return):
    return_id = f"RET-{i+1:06d}"
    borrow_date = datetime.datetime.strptime(borrow['borrowedAt'], "%Y-%m-%d %H:%M:%S")
    return_date = borrow_date + timedelta(days=random.randint(1, 14)) # Return within 2 weeks
    
    return_transactions.append({
        "id": return_id,
        "borrowId": borrow['id'],
        "adminId": random.choice(admin_ids),
        "returnedAt": return_date.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Find details for this borrow
    details = [d for d in borrow_details if d['borrowId'] == borrow['id']]
    
    for detail in details:
        return_details.append({
            "id": str(uuid.uuid4()),
            "returnId": return_id,
            "bookItemId": detail['bookItemId'],
            "conditionAtReturn": "Good", # Simplify
            "notes": random.choice(["", "", "Late return", "Damaged cover"])
        })
        item_status_map[detail['bookItemId']] = "Available"
        
    # Update borrow status
    borrow['status'] = "Returned"

# Update borrow_transactions.csv with new status
write_csv("borrow_transactions.csv", ["id", "adminId", "studentId", "borrowedAt", "dueDate", "status"], borrow_transactions)
write_csv("return_transactions.csv", ["id", "borrowId", "adminId", "returnedAt"], return_transactions)
write_csv("return_details.csv", ["id", "returnId", "bookItemId", "conditionAtReturn", "notes"], return_details)

# Update book_items.csv with final status
for item in book_items:
    item['status'] = item_status_map[item['id']]

write_csv("book_items.csv", ["id", "masterId", "code", "condition", "status", "createdAt"], book_items)

print("Data generation complete.")
