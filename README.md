# Where is SONY?

https://schufot.github.io/where-is-sony/

An overview of "SONY" tags in Cologne. I do not make them, I just take pictures of them.

## Technologies Used

- [python](https://www.python.org/)
- [Folium](https://python-visualization.github.io/folium/latest/)
- [GeoPandas](https://geopandas.org/en/stable/index.html)
- [SQLite](https://www.sqlite.org/)

## Screenshots

![where-is-sony-screenshot-1](https://github.com/user-attachments/assets/40b6119f-7abe-455d-af4c-d4ba28f627dd)
![where-is-sony-screenshot-2](https://github.com/user-attachments/assets/2f5d1d99-f7af-45c7-8483-02ec7c223987)
![where-is-sony-screenshot-3](https://github.com/user-attachments/assets/1ad269d7-87c8-4e73-8df0-289ae589e40d)

## Screencast

https://github.com/user-attachments/assets/0b40ca5e-5322-428e-a61d-61fb486e9503

## Add a new point

1. Get the coordinates:
   Go to Google Maps
   Right-click on the location you want to mark
   The coordinates will appear at the top of the menu
   Click to copy them

2. Prepare your image:
   Take a photo or select an existing one
   Note down the full path to the image file
   For example: /home/yourusername/Pictures/my_photo.jpg

3. Run the point manager:

```bash
python point_manager.py

```

4. Choose option 1 to add a new point and follow the prompts:

```bash
Point Manager
1. Add new point
2. List all points
3. Delete a point
4. Exit

Choose an option: 1

Enter latitude: 50.9147
Enter longitude: 6.9674
Enter description (max 50 chars): Beautiful view of the Rhine river
Enter path to image file: /path/to/your/image.jpg

```

5. After adding the point, regenerate the map:

```bash
python main.py

```

6. Open cologne_interactive.html in your web browser to see the result.

The point should appear as a red marker on your map. When you click it, you'll see your image and description in a popup.
