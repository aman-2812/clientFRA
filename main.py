import uvicorn
import pickle
from fastapi import FastAPI, HTTPException
import base64
from pydantic import BaseModel

import client_fra

app = FastAPI()

class WeightsData(BaseModel):
    weights: str

bucket_name = 'fra-5g-nw'
object_name = 'Traffic_Train_Data.csv'
local_file_path = '/app/Traffic_Train_Data.csv'
client_fra.download_file_from_s3(bucket_name, object_name, local_file_path)

@app.get("/")
async def root():
    return {"message": "Hello from FRA server"}

@app.post("/local_training")
async def test(weights_data: WeightsData):
    base64_encoded_weights = weights_data.weights
    # Convert the base64-encoded string back to bytes.
    serialized_weights = base64.b64decode(base64_encoded_weights)
    # Deserialize the weights using Pickle.
    try:
        global_weights = pickle.loads(serialized_weights)
    except pickle.UnpicklingError as e:
        raise HTTPException(status_code=400, detail="Invalid weights data")
    result = client_fra.local_training(global_weights)
    print(f"Returning result for {result[0]}")
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8010)