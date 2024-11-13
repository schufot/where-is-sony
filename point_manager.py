import sqlite3
from pathlib import Path
import shutil
import os

def setup_database():
    """Create SQLite database and necessary tables"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_point(latitude, longitude, description, image_path):
    """Add a new point to the database"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO points (latitude, longitude, description, image_path)
        VALUES (?, ?, ?, ?)
    ''', (latitude, longitude, description, image_path))
    
    conn.commit()
    conn.close()

def add_new_point():
    """Interactive function to add a new point to the database"""
    print("Add a new point to the map")
    print("--------------------------")
    
    try:
        # Get point information
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))
        description = input("Enter description (max 50 chars): ")[:50]
        
        # Handle image
        while True:
            image_path = input("Enter path to image file: ")
            if os.path.exists(image_path):
                # Create images directory if it doesn't exist
                Path("images").mkdir(exist_ok=True)
                
                # Copy image to images directory with a unique name
                file_extension = Path(image_path).suffix
                new_filename = f"point_{latitude}_{longitude}{file_extension}"
                new_path = os.path.join("images", new_filename)
                
                shutil.copy2(image_path, new_path)
                
                # Add to database
                add_point(latitude, longitude, description, new_path)
                print("Point added successfully!")
                break
            else:
                print("Image file not found. Please try again.")
                
    except Exception as e:
        print(f"Error adding point: {e}")
        # Clean up image if database insert failed
        if 'new_path' in locals() and os.path.exists(new_path):
            os.remove(new_path)

def list_all_points():
    """List all points in the database"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM points')
    points = c.fetchall()
    
    print("\nAll Points")
    print("-----------")
    for point in points:
        print(f"ID: {point[0]}")
        print(f"Location: {point[1]}, {point[2]}")
        print(f"Description: {point[3]}")
        print(f"Image: {point[4]}")
        print(f"Created: {point[5]}")
        print("-----------")
    
    conn.close()

def main():
    # Setup database when script starts
    setup_database()
    
    while True:
        print("\nPoint Manager")
        print("1. Add new point")
        print("2. List all points")
        print("3. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == "1":
            add_new_point()
        elif choice == "2":
            list_all_points()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()