from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import rclpy
import torch
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image

class CSDDInferenceNode(Node):
    def __init__(self):
        super().__init__('csdd_inference_node')

        self.yolov5_repo = Path('/home/arya-kshirsagar/ME222/belt2_ws/src/yolov5')
        self.weights_path = (
            self.yolov5_repo / 'runs/train/CSDD_Model/weights/best.pt'
        )
        self.capture_root = Path('/home/arya-kshirsagar/ME222/belt2_ws/src/csdd_captures')
        self.input_dir = self.capture_root / 'input'
        self.output_dir = self.capture_root / 'output'
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.model = torch.hub.load(
            str(self.yolov5_repo),
            'custom',
            path=str(self.weights_path),
            source='local'
        )
        self.bridge = CvBridge()
        self.box_spawn_x = 2.0
        self.camera_x = 0.0
        self.belt_speed = 0.3
        self.capture_delay_sec = abs(self.box_spawn_x - self.camera_x) / self.belt_speed
        self.center_tolerance_x = 0.08
        self.center_tolerance_y = 0.20
        self.capture_armed = True

        self.subscription = self.create_subscription(
            Image,
            '/belt_camera/image_raw',
            self.image_callback,
            10)

        self.start_time = self.get_clock().now()
        self.get_logger().info('CSDD Inference Node started. Waiting for images...')
        self.get_logger().info(f'Using weights: {self.weights_path}')
        self.get_logger().info(f'Input images will be saved to: {self.input_dir}')
        self.get_logger().info(f'Output images will be saved to: {self.output_dir}')
        self.get_logger().info(
            f'Capture delay set to about {self.capture_delay_sec:.2f}s based on spawn and belt speed'
        )

    def image_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(cv_image)
        annotated_frame = np.squeeze(results.render())

        elapsed_sec = (
            self.get_clock().now() - self.start_time
        ).nanoseconds / 1e9
        centered_detection = self.is_box_centered(cv_image, results)

        if centered_detection and elapsed_sec >= self.capture_delay_sec and self.capture_armed:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            input_path = self.input_dir / f'box_{timestamp}.png'
            output_path = self.output_dir / f'box_{timestamp}_defects.png'

            cv2.imwrite(str(input_path), cv_image)
            cv2.imwrite(str(output_path), annotated_frame)

            self.capture_armed = False
            self.get_logger().info(
                f'Captured full box and saved {input_path.name} / {output_path.name}'
            )
        elif not centered_detection:
            self.capture_armed = True

        cv2.imshow('Conveyor Belt Defect Detection', annotated_frame)
        cv2.waitKey(1)

    def is_box_centered(self, image, results):
        predictions = results.xyxy[0]
        if predictions is None or len(predictions) == 0:
            return False

        image_height, image_width = image.shape[:2]
        image_center_x = image_width / 2.0
        image_center_y = image_height / 2.0

        best_area = 0.0
        best_center_offset_x = 1.0
        best_center_offset_y = 1.0

        for pred in predictions:
            x1, y1, x2, y2 = pred[:4].tolist()
            box_width = max(0.0, x2 - x1)
            box_height = max(0.0, y2 - y1)
            area = box_width * box_height

            box_center_x = (x1 + x2) / 2.0
            box_center_y = (y1 + y2) / 2.0
            center_offset_x = abs(box_center_x - image_center_x) / image_width
            center_offset_y = abs(box_center_y - image_center_y) / image_height

            if area > best_area:
                best_area = area
                best_center_offset_x = center_offset_x
                best_center_offset_y = center_offset_y

        return (
            best_area > 0.0 and
            best_center_offset_x <= self.center_tolerance_x and
            best_center_offset_y <= self.center_tolerance_y
        )

def main(args=None):
    rclpy.init(args=args)
    node = CSDDInferenceNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
