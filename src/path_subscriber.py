#!/usr/bin/env python

import rospy
from custom_msgs.msg import Path

def path_callback(msg):
    rospy.loginfo(f"Received Path: {msg.path}")
    rospy.loginfo(f"New Path Flag: {msg.new_path}")
    rospy.loginfo(f"Stop Flag: {msg.stop}")

def subscriber():
    # Initialize the ROS node
    rospy.init_node('path_subscriber', anonymous=True)

    # Subscribe to the topic publishing the custom Path message
    rospy.Subscriber('path_topic', Path, path_callback)

    # Keep the node running
    rospy.spin()

if __name__ == '__main__':
    try:
        subscriber()
    except rospy.ROSInterruptException:
        pass
