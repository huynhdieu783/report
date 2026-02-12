import cv2
import mediapipe as mp
import math
def calculate_angle_with_horizontal(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    angle_rad = math.atan2(abs(dy), abs(dx))
    angle_degrees = math.degrees(angle_rad)
    return angle_degrees

def draw_point_and_text(img, x, y, text, color):
    cv2.circle(img, (x, y), 6, color, -1)
    cv2.putText(img, text, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)


def draw_angle_info(img, x, y, angle_name, angle_value, color):
    text = f"{angle_name}: {angle_value:.1f} do"
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


def main():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không thể mở camera")
        return

    print("Camera đã sẵn sàng. Nhấn 'q' để thoát.")

    with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    ) as pose:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Không đọc được frame")
                break

            h, w, _ = frame.shape
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            results = pose.process(image_rgb)
            image_rgb.flags.writeable = True
            image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                # Vẽ skeleton
                mp_drawing.draw_landmarks(
                    image_bgr,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                lm = results.pose_landmarks.landmark

                left_ear = lm[mp_pose.PoseLandmark.LEFT_EAR]
                left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]

                ear_x, ear_y = int(left_ear.x * w), int(left_ear.y * h)
                sh_x, sh_y = int(left_shoulder.x * w), int(left_shoulder.y * h)
                hip_x, hip_y = int(left_hip.x * w), int(left_hip.y * h)

                draw_point_and_text(image_bgr, ear_x, ear_y, f"Ear ({ear_x},{ear_y})", (255, 217, 102))
                draw_point_and_text(image_bgr, sh_x, sh_y, f"Shoulder ({sh_x},{sh_y})", (61, 133, 198))
                draw_point_and_text(image_bgr, hip_x, hip_y, f"Hip ({hip_x},{hip_y})", (0, 0, 0))

                cv2.line(image_bgr, (ear_x, ear_y), (sh_x, sh_y), (56, 118, 29), 2)
                cv2.line(image_bgr, (sh_x, sh_y), (hip_x, hip_y), (103,78,167), 2)
                cv2.line(image_bgr, (ear_x - 50, ear_y), (ear_x + 50, ear_y), (128, 128, 128), 1)
                cv2.line(image_bgr, (sh_x - 50, sh_y), (sh_x + 50, sh_y), (128, 128, 128), 1)

                alpha = calculate_angle_with_horizontal(
                    (ear_x, ear_y),  # Tai
                    (sh_x, sh_y)  # Vai
                )

                beta = calculate_angle_with_horizontal(
                    (sh_x, sh_y),  # Vai
                    (hip_x, hip_y)  # Hông
                )

                draw_angle_info(image_bgr, 30, 50, "Alpha (Tai-Vai)", alpha, (56, 118, 29))
                draw_angle_info(image_bgr, 30, 90, "Beta (Vai-Hong)", beta, (103,78,167))

                mid_x = (ear_x + sh_x) // 2
                mid_y = (ear_y + sh_y) // 2
                cv2.putText(image_bgr, f"a={alpha:.1f}°",
                            (mid_x + 10, mid_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (56, 118, 29), 2)

                # Vẽ góc beta tại vị trí giữa Vai và Hông
                mid_x2 = (sh_x + hip_x) // 2
                mid_y2 = (sh_y + hip_y) // 2
                cv2.putText(image_bgr, f"b={beta:.1f}°",
                            (mid_x2 + 10, mid_y2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (103,78,167), 2)

            cv2.imshow("PHAT HIEN TU THE - TINH GOC", image_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
