from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi import APIRouter
from PIL import Image
import numpy as np
import keras
import io

ml_router = APIRouter()
plague_net_model = keras.models.load_model('./static/plague_net_model_final.keras')

@ml_router.post("/plague-net/predict")
async def predict_plague_net(file: UploadFile = File(...)):
    class_names = ['Chinche salivosa', 'Clororis', 'Hoja sana', 'Roya naranja', 'Roya purpura']

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        image = image.convert("RGB")
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = plague_net_model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]
        class_name = class_names[predicted_class]
        confidence = np.max(predictions)

        return {"prediction": class_name, "confidence": float(confidence)}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la imagen: {str(e)}")