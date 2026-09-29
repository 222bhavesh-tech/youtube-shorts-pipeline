import os, sys

print("=== MediaPipe ===")
try:
    import mediapipe as mp
    print("mp version:", getattr(mp, "__version__", "?"))
    print("has legacy solutions:", hasattr(mp, "solutions"))
    try:
        from mediapipe.tasks.python import vision
        print("tasks.vision import: OK")
    except Exception as e:
        print("tasks.vision import FAILED:", e)
    # legacy probe
    try:
        _ = mp.solutions.face_detection.FaceDetection
        print("legacy FaceDetection: OK")
    except Exception as e:
        print("legacy FaceDetection FAILED:", type(e).__name__)
except Exception as e:
    print("mediapipe import FAILED:", e)

print("=== OpenCV fallback ===")
try:
    import cv2
    d = getattr(cv2, "data", None)
    fp = os.path.join(d.haarcascades, "haarcascade_frontalface_default.xml") if d else ""
    print("cv2:", cv2.__version__)
    print("haar cascade exists:", fp if fp and os.path.exists(fp) else "NOT FOUND")
except Exception as e:
    print("cv2 FAILED:", e)

print("=== .task model present? ===")
found = []
for root, dirs, files in os.walk(r"D:\youtube system"):
    for f in files:
        if f.endswith(".task"):
            found.append(os.path.join(root, f))
print(found[:5] if found else "none")
