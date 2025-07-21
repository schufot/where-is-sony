# Where is SONY?

https://schufot.github.io/where-is-sony/

An overview of "SONY 678" tags in Cologne. I do not make them, I just take pictures of them.

## Technologies Used

- [python](https://www.python.org/)
- [Folium](https://python-visualization.github.io/folium/latest/)
- [GeoPandas](https://geopandas.org/en/stable/index.html)
- [SQLite](https://www.sqlite.org/)

## Screenshots

![where-is-sony-screenshot-1](https://github.com/user-attachments/assets/f85e7596-18e0-4ef9-9f4b-e826caa7f774)
![where-is-sony-screenshot-2](https://github.com/user-attachments/assets/90e6138a-a854-4e02-99e0-79fe4ce194c5)
![where-is-sony-screenshot-3](https://github.com/user-attachments/assets/5c6a43c7-0310-43ae-9736-cf97df6f3878)
![where-is-sony-screenshot-4](https://github.com/user-attachments/assets/0ae8f671-b73e-43d9-a795-390ee79ac018)
![where-is-sony-screenshot-5](https://github.com/user-attachments/assets/24cc25a0-16f1-4630-92bf-7a3016109155)

## Screencast

https://github.com/user-attachments/assets/47b92b54-9aee-4e2b-9a9d-ffa086177dbf

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

## Sources

- [Cologne boundaries](https://offenedaten-koeln.de/dataset/stadtgebiet-k%C3%B6ln/resource/6a24870c-7e7a-4f16-95e2-a110d50d6598)
