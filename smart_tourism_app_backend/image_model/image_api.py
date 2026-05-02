import io
import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO

app = FastAPI(title="Visual Sensing API", description="Smart Tourism - Visual Sensing (Image Model)")

import sys
import os

# Allow importing from noise_model
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'noise_model'))
from inference import load_model, classify
from preprocess import SAMPLE_RATE

# Load the YOLOv8 model for person detection
yolo_model = YOLO('yolov8n.pt')

# Load the Noise Classification TFLite/Keras model
NOISE_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'noise_model', 'noise_model_best.h5')
noise_model = load_model(NOISE_MODEL_PATH)

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def process_crowd_image(img_bytes: bytes) -> int:
    """
    Decodes image bytes, blurs faces for privacy, and counts persons using YOLOv8.
    """
    # Decode image bytes into an OpenCV format
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file")

    # Detect faces and apply a Gaussian Blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        # Apply severe blur to the face region for privacy
        face_roi = img[y:y+h, x:x+w]
        blur = cv2.GaussianBlur(face_roi, (99, 99), 30)
        img[y:y+h, x:x+w] = blur
        
    # Run the blurred image through YOLOv8 targeting "person" (class 0)
    # We specify conf=0.5 and classes=[0] to filter for persons only
    results = yolo_model(img, conf=0.5, classes=[0], verbose=False)
    
    # Count persons
    person_count = 0
    for result in results:
        # result.boxes contains the bounding boxes
        person_count += len(result.boxes)
        
    return person_count

@app.post("/analyze-crowd")
async def analyze_crowd(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        person_count = process_crowd_image(img_bytes)
        
        return JSONResponse(content={
            "status": "success",
            "detected_person_count": person_count,
            "privacy_status": "Facial blurring applied",
            "message": "Crowd density calculated via Visual Sensing"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

@app.post("/analyze-noise")
async def analyze_noise(file: UploadFile = File(...)):
    try:
        # Save the uploaded audio file temporarily
        import tempfile
        import soundfile as sf
        
        audio_bytes = await file.read()
        
        # Write to a temporary file
        fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(audio_bytes)
                
            # Use soundfile to read the audio so we can measure it
            # then pass the audio array to classify() which can handle it 
            audio_data, sample_rate = sf.read(temp_audio_path)
            
            # Ensure it is mono (flattened)
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            # Pass to the noise model classifier
            # We don't want it to record, we want to provide the audio directly
            noise_result = classify(
                model=noise_model,
                audio=audio_data.astype('float32'),
                location_id="flutter-client",
                sample_rate=sample_rate
            )
            
            signal = noise_result['acoustic_signal']
            is_crowded = signal['is_crowded']
            
            # Decide the person count to return to Flutter based on prediction
            # If the noise model says 'crowd' & 'is_crowded', we return a high number to trigger nudging.
            # (In a fully hybrid system, you'd combine YOLO + Noise results)
            simulated_count = 120 if is_crowded else 45
            status_message = (
                "Ambient noise classified as 'High Crowd' (loud)" if is_crowded 
                else "Ambient noise classified as 'Calm Nature'"
            )

            return JSONResponse(content={
                "status": "success",
                "detected_person_count": simulated_count, 
                "privacy_status": "Secure - Analyzed locally without storing audio",
                "message": status_message,
                "noise_details": {
                    "label": signal['label'],
                    "confidence": signal['confidence'],
                    "db_level": signal['db_level'],
                }
            })
        finally:
            os.remove(temp_audio_path)
            
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    uvicorn.run("image_api:app", host="0.0.0.0", port=8000, reload=True)
