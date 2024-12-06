import sqlite3
from pathlib import Path
import shutil
import os

# TODO: Remove description

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

def delete_point(point_id):
    """Delete a point and its associated image"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    # First get the image path
    c.execute('SELECT image_path FROM points WHERE id = ?', (point_id,))
    result = c.fetchone()
    
    if result:
        image_path = result[0]
        
        # Delete from database
        c.execute('DELETE FROM points WHERE id = ?', (point_id,))
        conn.commit()
        
        # Delete associated image file
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Point {point_id} and its image were deleted successfully!")
        else:
            print(f"Point {point_id} was deleted, but image file was not found.")
    else:
        print(f"No point found with ID {point_id}")
    
    conn.close()

def add_new_point():
    """Interactive function to add a new point to the database"""
    print("\nAdd a new point to the map")
    print("--------------------------")
    
    try:
        latitude = float(input("Enter latitude: "))
        longitude = float(input("Enter longitude: "))
        description = input("Enter description (max 50 chars): ")[:50]
        
        while True:
            image_path = input("Enter path to image file: ")
            if os.path.exists(image_path):
                Path("images").mkdir(exist_ok=True)
                file_extension = Path(image_path).suffix
                new_filename = f"point_{latitude}_{longitude}{file_extension}"
                new_path = os.path.join("images", new_filename)
                
                shutil.copy2(image_path, new_path)
                add_point(latitude, longitude, description, new_path)
                print("Point added successfully!")
                break
            else:
                print("Image file not found. Please try again.")
                
    except Exception as e:
        print(f"Error adding point: {e}")
        if 'new_path' in locals() and os.path.exists(new_path):
            os.remove(new_path)

def list_all_points():
    """List all points in the database"""
    conn = sqlite3.connect('map_points.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM points')
    points = c.fetchall()
    
    if not points:
        print("\nNo points found in database.")
        return
    
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

def delete_point_interactive():
    """Interactive function to delete a point"""
    print("\nDelete a point")
    print("-------------")
    
    # First show all points
    list_all_points()
    
    try:
        point_id = int(input("\nEnter the ID of the point to delete (or 0 to cancel): "))
        if point_id == 0:
            print("Deletion cancelled.")
            return
            
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete point {point_id}? (yes/no): ")
        if confirm.lower() == 'yes':
            delete_point(point_id)
        else:
            print("Deletion cancelled.")
            
    except ValueError:
        print("Please enter a valid number.")
    except Exception as e:
        print(f"Error deleting point: {e}")

def main():
    setup_database()
    
    while True:
        print("\nPoint Manager")
        print("1. Add new point")
        print("2. List all points")
        print("3. Delete a point")
        print("4. Exit")
        
        choice = input("\nChoose an option: ")
        
        if choice == "1":
            add_new_point()
        elif choice == "2":
            list_all_points()
        elif choice == "3":
            delete_point_interactive()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()