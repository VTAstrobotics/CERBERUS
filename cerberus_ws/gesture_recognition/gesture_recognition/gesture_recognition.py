
import cv2
import numpy as np
import rclpy  # Import the ROS 2 Python client library
import os
from ament_index_python.packages import get_package_share_directory
from ultralytics import YOLO
from cv_bridge import CvBridge  # Import CvBridge to convert between ROS and OpenCV images
from rclpy.node import Node
from sensor_msgs.msg import Image  # Import the Image message type from sensor_msgs
from std_msgs.msg import Int32
# --------------------------------------------------
# Configuration
# --------------------------------------------------

pkg_share = get_package_share_directory('gesture_recognition')
MODEL_PATH = os.path.join(pkg_share, 'resource', 'yolo11n-pose.pt')
CAMERA_INDEX = 0
CONFIDENCE_THRESHOLD = 0.5

# COCO body-keypoint indices
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_ELBOW = 7
RIGHT_ELBOW = 8
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12
LEFT_KNEE = 13
RIGHT_KNEE = 14
LEFT_ANKLE = 15
RIGHT_ANKLE = 16

# --------------------------------------------------
# Load model
# --------------------------------------------------

model = YOLO(MODEL_PATH)

# --------------------------------------------------
# Ros Node
# --------------------------------------------------

class GestureNode(Node):
    def __init__(self):
        super().__init__('gesture_node')
        self.publisher = self.create_publisher(Int32, f'/pose', 10)
        self.subscription = self.create_subscription(Image, f'image_raw', self.image_callback, 10)
        self.bridge = CvBridge()  # Initialize the CvBridge to convert between ROS and OpenCV images

        
# --------------------------------------------------
# Main webcam loop
# --------------------------------------------------

    def image_callback(self,img):
        frame = self.bridge.imgmsg_to_cv2(img,encoding="bgr8")
        #crop
        height,width,_ = frame.shape
        half_width = width // 2
        frame = frame[:, :half_width]

        img_h, img_w, _ = frame.shape
        
        # Estimate body keypoints for every detected person.
        results = model.predict(
            source=frame,
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )

        result = results[0]

        # Draw YOLO's pose skeletons and person detections.
        annotated_frame = result.plot()

        if result.keypoints is not None:
            all_keypoints = result.keypoints.xy.cpu().numpy()
            all_confidences = (
                result.keypoints.conf.cpu().numpy()
                if result.keypoints.conf is not None
                else None
            )

            boxes = (
                result.boxes.xyxy.cpu().numpy()
                if result.boxes is not None
                else []
            )

            for i, points in enumerate(all_keypoints):
                if all_confidences is None:
                    gesture = -1
                else:
                    gesture = self.classify_gesture(
                        points, all_confidences[i]
                    )
                #publish gesture
                rosmsg = Int32()
                rosmsg.data = gesture
                self.publisher.publish(rosmsg)
                # Place gesture label above the person.
                if len(boxes) > i:
                    x1, y1, _, _ = boxes[i].astype(int)
                    label_x = max(0, x1)
                    label_y = max(30, y1 - 10)
                else:
                    label_x, label_y = 10, 30 + i * 30

                cv2.putText(
                    annotated_frame,
                    str(gesture),
                    (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA
                )
        


    def distance(self, point_a, point_b):
        """Euclidean distance between two 2D points."""
        return np.linalg.norm(point_a - point_b)


    def classify_gesture(self, keypoints, confidences):
        """
        Classify a person's pose into one of 5 distinct long-range gestures:
        1. Hands Raised
        2. One Hand Raised (Either left or right)
        3. T-Pose
        4. Hands on Hips
        5. Crouch
        Returns the gesture name or 'No Gesture'.
        """

        # We require the upper body and hips for most gestures.
        # Knees are checked dynamically later so partial occlusion doesn't break everything.
        required = [
            LEFT_SHOULDER, RIGHT_SHOULDER,
            LEFT_ELBOW, RIGHT_ELBOW,
            LEFT_WRIST, RIGHT_WRIST,
            LEFT_HIP, RIGHT_HIP
        ]

        # Require visible landmarks before classifying.
        if any(confidences[i] < CONFIDENCE_THRESHOLD for i in required):
            return -1

        ls = keypoints[LEFT_SHOULDER]
        rs = keypoints[RIGHT_SHOULDER]
        le = keypoints[LEFT_ELBOW]
        re = keypoints[RIGHT_ELBOW]
        lw = keypoints[LEFT_WRIST]
        rw = keypoints[RIGHT_WRIST]
        lh = keypoints[LEFT_HIP]
        rh = keypoints[RIGHT_HIP]
        rk = keypoints[RIGHT_KNEE]
        lk = keypoints[LEFT_KNEE]
        ra = keypoints[RIGHT_ANKLE]
        la = keypoints[LEFT_ANKLE]

        shoulder_width = self.distance(ls, rs)
        if shoulder_width < 4:
            return -1

        # Image coordinates: smaller y means higher on screen.
        shoulder_y = (ls[1] + rs[1]) / 2.0
        hip_y = (lh[1] + rh[1]) / 2.0
        torso_height = hip_y - shoulder_y

        ankle_distance = self.distance(la, ra)

        if torso_height < 6:
            return -1

        # --------------------------------------------------
        # 0. CROUCH
        # --------------------------------------------------
        knees_confident = (
            confidences[LEFT_KNEE] > CONFIDENCE_THRESHOLD 
            and confidences[RIGHT_KNEE] > CONFIDENCE_THRESHOLD
        )
        
        if knees_confident:
            lk = keypoints[LEFT_KNEE]
            rk = keypoints[RIGHT_KNEE]
            knee_y = (lk[1] + rk[1]) / 2.0
            
            # When standing straight, knee_y is ~1 torso_height below hip_y.
            # When crouching, the femur is horizontal, compressing the vertical gap.
            if (knee_y - hip_y) < 0.40 * torso_height:
                return 0

        # --------------------------------------------------
        # Camera Direction & Anatomical Side Resolution
        # --------------------------------------------------
        outward_dir = 1.0 if ls[0] >= rs[0] else -1.0

        # Positive values mean the joint is extended outward away from the torso
        le_outward = (le[0] - ls[0]) * outward_dir
        lw_outward = (lw[0] - ls[0]) * outward_dir
        re_outward = (rs[0] - re[0]) * outward_dir
        rw_outward = (rs[0] - rw[0]) * outward_dir

        # --------------------------------------------------
        # Vertical Zones (Normalized by torso_height)
        # --------------------------------------------------
        raised_margin = 0.20 * torso_height
        left_wrist_high = lw[1] < (ls[1] - raised_margin)
        right_wrist_high = rw[1] < (rs[1] - raised_margin)

        # Horizontal arm up thresholds (Wrist must be directly above shoulder)
        aligned_margin = 0.30 * torso_height
        left_wrist_aligned = (ls[0] + aligned_margin) > le[0] > (ls[0] - aligned_margin)
        right_wrist_aligned = (rs[0] + aligned_margin) > re[0] > (rs[0] - aligned_margin)

        # Neutral "arm down" threshold: wrist is well below chest level
        arm_down_y = shoulder_y + 0.55 * torso_height
        left_wrist_down = lw[1] > arm_down_y
        right_wrist_down = rw[1] > arm_down_y

        # --------------------------------------------------
        # 1. HANDS RAISED (Both hands up)
        # --------------------------------------------------
        if left_wrist_high and left_wrist_aligned and right_wrist_high and right_wrist_aligned:
            return 1

        # --------------------------------------------------
        # 2. STAR (Hands up diagonally, legs out diagonally)
        # --------------------------------------------------
        t_vertical_tol = 0.60 * torso_height #0.35 orgiinal

        angleOfLeftArm = np.arctan2(ls[1] - le[1], ls[0] - le[0]) * 180 / np.pi
        angleOfRightArm = np.arctan2(rs[1] - re[1], rs[0] - re[0]) * 180 / np.pi
        arms_at_45 = (
            140 < angleOfLeftArm < 180
            and 20 < angleOfRightArm < 60
        )

        left_arm_straight_out = (
            le_outward > 0.15 * shoulder_width
            and lw_outward > le_outward
            and lw_outward > 0.65 * shoulder_width
        )
        right_arm_straight_out = (
            re_outward > 0.15 * shoulder_width
            and rw_outward > re_outward
            and rw_outward > 0.65 * shoulder_width
        )

        leg_tolerance = shoulder_width * 0.55

        if ankle_distance > shoulder_width + leg_tolerance and arms_at_45:
            return 2

        # --------------------------------------------------
        # 3. T-POSE (Both arms extended straight out at shoulder level)
        # --------------------------------------------------
        t_vertical_tol = 0.25 * torso_height

        arms_at_shoulder_height = (
            abs(le[1] - ls[1]) < t_vertical_tol
            and abs(lw[1] - ls[1]) < t_vertical_tol
            and abs(re[1] - rs[1]) < t_vertical_tol
            and abs(rw[1] - rs[1]) < t_vertical_tol
        )

        left_arm_straight_out = (
            le_outward > 0.15 * shoulder_width
            and lw_outward > le_outward
            and lw_outward > 1 * shoulder_width
        )
        right_arm_straight_out = (
            re_outward > 0.15 * shoulder_width
            and rw_outward > re_outward
            and rw_outward > 1 * shoulder_width
        )

        if arms_at_shoulder_height and left_arm_straight_out and right_arm_straight_out:
            return 3


        # --------------------------------------------------
        # 4. FLEX (Both arms Flexing)
        # --------------------------------------------------
        t_vertical_tol = 0.20 * torso_height

        arms_at_shoulder_height = (
            abs(le[1] - ls[1]) < t_vertical_tol
            and abs(re[1] - rs[1]) < t_vertical_tol
        )

        align_wrists_and_elbows = (
            le[0] - lw[0] < t_vertical_tol
            and re[0] - rw[0] < t_vertical_tol
        )

        if arms_at_shoulder_height and align_wrists_and_elbows:
            return 4

        return -1




def main(args=None):
    rclpy.init(args=args)  # Initialize the ROS 2 Python client library
    node = GestureNode()  # Create an instance of the CameraNode
    try:
        rclpy.spin(node)  # Spin the node to keep it alive and processing callbacks
    except KeyboardInterrupt:
        pass  # Allow the user to exit with Ctrl+C
    finally:
        node.destroy_node()  # Destroy the ROS 2 node
        rclpy.shutdown()  # Shut down the ROS 2 Python client library

        
if __name__ == '__main__':
    main()  # Run the main function if this script is executed
