# ReadMe.md

Author: Akshay Naik  
Date: 11/08/24 

## Overview
Processes ROS 2 bag data to extract yaw, pitch, roll, GPS coordinates, and obstacle maps, saving results in `saved_data/data.pkl`.

## Requirements
Refer to `requirements.txt` for the full list of dependencies. Install them with:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Add your ROS 2 bag folder to `rosbag_data`.
2. Update `bag_path` in `bag_parse.py`.
4. Run:
   ```bash
   python src/bag_parse.py
   ```

## Notes
- The script generates data.pkl containing parsed data, stored in saved_data.
- Customize bag_parse.py as needed for different data extraction needs or additional processing.
- Feel free to add more topic parsing and msg files as needed.