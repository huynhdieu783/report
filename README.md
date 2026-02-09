# report
# báo cáo giữa kì KTLT
# mediapipe 0.10.32
import cv2
import mediapipe as mp
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("Đang kiểm tra kết nối... Nhấn 'q' để dừng.")
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose_estimator:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Đang đợi tín hiệu từ camera...")
            continue

        # Xử lý hình ảnh
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_estimator.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Vẽ skeleton
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS
            )

        cv2.imshow("TEST CAMERA - STEP 3", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
