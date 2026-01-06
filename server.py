from fastapi import FastAPI
from api_data_extraction import fetch_api_data,save_json ,extract_lists,OUTPUT_FOLDER 
import os 
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/api1")
async def tool():
    return {"message": "Hello tool"}
@app.get("/api2/v1")
async def ky():
    print("Fetching data from API...")
    data = fetch_api_data()
    if data:
        save_json(data, os.path.join(OUTPUT_FOLDER, "api_response.json"))
        extract_lists(data)
    else:
        print("Failed to fetch API data.")
    return {"data": data }

