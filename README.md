import cv2
import mediapipe as mp
import math


mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(p1, p2):
    """Tính góc của đoạn thẳng nối p1, p2 so với phương thẳng đứng (độ)"""
    # p1, p2 là tuple (x, y)
    dist_x = p2[0] - p1[0]
    dist_y = p2[1] - p1[1]
  
    angle_radians = math.atan2(dist_x, dist_y)
    angle_degrees = abs(math.degrees(angle_radians))
    return angle_degrees

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

   
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Lấy tọa độ các điểm cần thiết (sử dụng bên trái hoặc bên phải tùy góc nhìn)
        ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]

        # Tính góc
        angle_ear_shoulder = calculate_angle(ear, shoulder)
        angle_shoulder_hip = calculate_angle(shoulder, hip)

        # Logic kiểm tra tư thế
        status_text = "Tu the: Tot"
        color = (0, 255, 0) # Xanh lá

        if angle_ear_shoulder > 15:
            status_text = "SAI TU THE: NGANG DAU LEN!"
            color = (0, 0, 255) # Đỏ
        elif angle_shoulder_hip > 10:
            status_text = "SAI TU THE: NGOI THANG LEN!"
            color = (0, 0, 255) # Đỏ

        # Hiển thị thông báo lên màn hình
        cv2.putText(image, status_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(image, f"Goc Tai-Vai: {int(angle_ear_shoulder)} deg", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(image, f"Goc Vai-Hong: {int(angle_shoulder_hip)} deg", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Vẽ các điểm nối để dễ quan sát
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow('Kiem tra tu the', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
  
