# Report
# Báo cáo giữa kì KTLT
# Python 3.11
# mediapipe 0.10.32

import cv2
import mediapipe as mp

def draw_point_and_text(img, x, y, text, color):
    cv2.circle(img, (x, y), 6, color, -1)
    cv2.putText(
        img, text, (x + 5, y - 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1
    )

def main():
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(" Không thể mở camera")
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
                print(" Không đọc được frame")
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

                # Lấy vị trí Tai – Vai – Hông (bên trái)
                left_ear = lm[mp_pose.PoseLandmark.LEFT_EAR]
                left_shoulder = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]

                # Chuyển sang pixel
                ear_x, ear_y = int(left_ear.x * w), int(left_ear.y * h)
                sh_x, sh_y = int(left_shoulder.x * w), int(left_shoulder.y * h)
                hip_x, hip_y = int(left_hip.x * w), int(left_hip.y * h)

                # Vẽ điểm và tọa độ
                draw_point_and_text(image_bgr, ear_x, ear_y, f"Ear ({ear_x},{ear_y})", (255, 0, 0))
                draw_point_and_text(image_bgr, sh_x, sh_y, f"Shoulder ({sh_x},{sh_y})", (0, 255, 0))
                draw_point_and_text(image_bgr, hip_x, hip_y, f"Hip ({hip_x},{hip_y})", (0, 0, 255))

            cv2.imshow("TEST CAMERA - MEDIAPIPE POSE", image_bgr)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
