from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
"""
from autogluon.multimodal import MultiModalPredictor
from PIL import Image
import io

"""

ea_router = APIRouter()

"""
predictor = MultiModalPredictor.load('./components/ml_models/autogluon_plague_classifier')

ea_router.post("/predict",)
async def predict_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        rgb_image = image.convert("RGB")

        data = {'image': [rgb_image]}  # AutoGluon espera un DataFrame con las imágenes en este formato

        prediction = predictor.predict(data)
        print(prediction)
        return {"prediction": prediction[0]}  # Devolver la predicción
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la imagen: {str(e)}")

"""