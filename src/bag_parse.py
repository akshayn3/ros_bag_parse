from pathlib import Path
import pickle
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
import numpy as np
import matplotlib.pyplot as plt


def guess_msgtype(path: Path) -> str:
    """Guess message type name from path."""
    name = path.relative_to(path.parents[2]).with_suffix('')
    if 'msg' not in name.parts:
        name = name.parent / 'msg' / name.name
    return str(name)

def add_custom_types(typestore):
    custom_msg_path = [
    './msg_files/vectornav_msgs/msg/CommonGroup.msg',
    './msg_files/vectornav_msgs/msg/InsStatus.msg', 
    ]

    add_types = {}
    for pathstr in custom_msg_path:
        msgpath = Path(pathstr)
        msgdef = msgpath.read_text(encoding='utf-8')
        add_types.update(get_types_from_msg(msgdef, guess_msgtype(msgpath)))
    typestore.register(add_types)


def get_posdata(msg):
    yaw = msg.yawpitchroll.x
    pitch = msg.yawpitchroll.y
    roll = msg.yawpitchroll.z

    lat = msg.position.x
    long = msg.position.y
    alt = msg.position.z
    
    return (yaw, pitch, roll), (lat, long, alt)
    
def get_image(msg):
    height = msg.height
    width = msg.width
    encoding = msg.encoding
    is_bigendian = msg.is_bigendian
    step = msg.step
    data = msg.data

    # OpenCV image
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            for k in range(3):
                image[i, j, k] = data[i*step + j*3 + k]

    return image

def main(bag_path):
    typestore = get_typestore(Stores.ROS2_HUMBLE)
    add_custom_types(typestore)
    # Trim path string to last folder name and remove prefix of rosbag2_
    pkl_folder = 'saved_data/' + bag_path.split('/')[-1][8:]

    ypr_pts = []
    gps_pts = []
    pos_time_pts = []

    obst_pts = []
    obst_time_pts = []

    topics = []

    start = None
    obst_map = None
    ypr = None
    gps = None

    with Reader(bag_path) as reader:
        print("Reading messages from", bag_path)
        for connection in reader.connections:
            topics.append(connection.topic)

        for connection, timestamp, rawdata in reader.messages():
            
            if connection.topic == '/vectornav/raw/common': # IMU
                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)

                ypr, gps = get_posdata(msg)
            
            if connection.topic == '/Obstacle_map': # Obstacle Map
                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
                obst_map = get_image(msg)
            
            if obst_map is not None and ypr is not None and gps is not None:
                ypr_pts.append(ypr)
                gps_pts.append(gps)
                pos_time_pts.append(timestamp)
                obst_pts.append(obst_map)
                obst_time_pts.append(timestamp)

                if start is None:
                    start = gps[:2]
                    init_yaw = ypr[0]
                    goal = (40.11380645884632, -88.30969735953262)
                
                obst_map = None
                ypr = None
                gps = None
                
    # Print topics
    print("Topics:")
    for topic in topics:
        print(topic)

    data = {
        'ypr_pts': ypr_pts,
        'gps_pts': gps_pts,
        'obst_pts': obst_pts,
        'pos_time_pts': pos_time_pts,
        'obst_time_pts': obst_time_pts
    }
    
    if not Path(pkl_folder).exists():
        Path(pkl_folder).mkdir(parents=True)

    data_path = pkl_folder + '/data.pkl'
    
    with open(data_path, 'wb') as f:
        pickle.dump(data, f)

if __name__ == '__main__':
    bag_path = "rosbag_data/rosbag2_2024_10_02-18_19_13"
    # Trim path string to last folder name and remove prefix of rosbag2_
    pkl_folder = 'saved_data/' + bag_path.split('/')[-1][8:]

    main(bag_path)
    
    data_path = pkl_folder + '/data.pkl'
    with open(data_path, 'rb') as f:
        print("Saving data to", data_path)
        data = pickle.load(f)
    
    ypr_pts = data['ypr_pts']
    gps_pts = data['gps_pts']
    obst_pts = data['obst_pts']
    pos_time_pts = data['pos_time_pts']
    obst_time_pts = data['obst_time_pts']
