import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

DB_PATH = os.path.join("data", "donations.db")

def get_connection():
    """Establishes a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    """Initializes the database with necessary tables."""
    conn = get_connection()
    c = conn.cursor()

    # Donations / Inventory Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER NOT NULL,
            unit TEXT,
            expiration_date TEXT,
            donor_name TEXT,
            entry_date TEXT,
            status TEXT DEFAULT 'Available' -- Available, Reserved, Dispatched, Expired
        )
    ''')

    # Kits Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS kits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kit_name TEXT NOT NULL,
            contents TEXT, -- JSON string of item composition
            quantity_assembled INTEGER DEFAULT 0,
            creation_date TEXT
        )
    ''')

    # Dispatches Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT,
            receiver_name TEXT,
            items_sent TEXT, -- JSON string of items/kits sent
            dispatch_date TEXT,
            status TEXT DEFAULT 'Pending' -- Pending, Completed, Cancelled
        )
    ''')

    conn.commit()
    conn.close()

def add_donation(item_name, category, quantity, unit, expiration_date, donor_name):
    """Adds a new donation to the inventory."""
    conn = get_connection()
    c = conn.cursor()
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO inventory (item_name, category, quantity, unit, expiration_date, donor_name, entry_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Available')
    ''', (item_name, category, quantity, unit, expiration_date, donor_name, entry_date))
    conn.commit()
    conn.close()

def get_inventory():
    """Returns the current inventory as a DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def assemble_kit(kit_name, items_recipe, quantity_to_make):
    """
    Assembles kits by deducting ingredients from inventory and adding the kit as a new item.
    items_recipe: list of dicts [{'item_name': 'Arroz', 'quantity_needed_per_kit': 2}, ...]
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # 1. Deduct ingredients
        for item in items_recipe:
            name = item['item_name']
            total_needed = item['quantity_needed_per_kit'] * quantity_to_make
            
            # Find available batches (FIFO logic optional, here we just take from available)
            # Querying simple aggregation for now
            # In a real WMS we'd pick specific batches. Here we will reduce from 'Available' entries.
            # Simplified: We treat items as fungible by name for this deduction.
            
            # Check availability
            c.execute("SELECT id, quantity FROM inventory WHERE item_name = ? AND status = 'Available' ORDER BY entry_date ASC", (name,))
            batches = c.fetchall()
            
            remaining_to_deduct = total_needed
            
            for batch_id, qty in batches:
                if remaining_to_deduct <= 0:
                    break
                
                if qty <= remaining_to_deduct:
                    # Minimize this batch to 0 (or delete?) -> Mark as Consumed?
                    # Let's reduce quantity. If 0, we can leave it or delete. 
                    # Keeping it 0 is safer for history, or mark status 'Consumed'
                    c.execute("UPDATE inventory SET quantity = 0, status = 'Consumed' WHERE id = ?", (batch_id,))
                    remaining_to_deduct -= qty
                else:
                    # Partial reduction
                    c.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (remaining_to_deduct, batch_id))
                    remaining_to_deduct = 0
            
            if remaining_to_deduct > 0:
                raise ValueError(f"No hay suficiente stock para {name}")

        # 2. Add Kit to Inventory
        entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit, donor_name, entry_date, status)
            VALUES (?, 'Kits', ?, 'Unidades', 'Sistema (Armado)', ?, 'Available')
        ''', (kit_name, quantity_to_make, entry_date))
        
        # 3. Log Kit Creation
        c.execute('''
            INSERT INTO kits (kit_name, contents, quantity_assembled, creation_date)
            VALUES (?, ?, ?, ?)
        ''', (kit_name, json.dumps(items_recipe), quantity_to_make, entry_date))

        conn.commit()
        return True, "Kit armado exitosamente"
        
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def create_dispatch(destination, receiver_name, items_to_dispatch):
    """
    Creates a dispatch order and deducts items from inventory.
    items_to_dispatch: list of dicts [{'item_name': 'Kit Básico', 'quantity': 5}, ...]
    """
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # 1. Deduct items
        for item in items_to_dispatch:
            name = item['item_name']
            total_needed = item['quantity']
            
            # Check availability
            c.execute("SELECT id, quantity FROM inventory WHERE item_name = ? AND status = 'Available' ORDER BY entry_date ASC", (name,))
            batches = c.fetchall()
            
            remaining_to_deduct = total_needed
            
            current_stock = sum([b[1] for b in batches])
            if current_stock < total_needed:
                 raise ValueError(f"No hay suficiente stock para {name}. Solicitado: {total_needed}, Disponible: {current_stock}")

            for batch_id, qty in batches:
                if remaining_to_deduct <= 0:
                    break
                
                if qty <= remaining_to_deduct:
                    # Fully consume batch
                    c.execute("UPDATE inventory SET quantity = 0, status = 'Dispatched' WHERE id = ?", (batch_id,))
                    remaining_to_deduct -= qty
                else:
                    # Partial reduction
                    c.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?", (remaining_to_deduct, batch_id))
                    remaining_to_deduct = 0
            
        # 2. Log Dispatch
        dispatch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO dispatches (destination, receiver_name, items_sent, dispatch_date, status)
            VALUES (?, ?, ?, ?, 'Completed')
        ''', (destination, receiver_name, json.dumps(items_to_dispatch), dispatch_date))

        conn.commit()
        return True, "Despacho realizado con éxito"
        
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()

