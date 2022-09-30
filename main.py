from fastapi import FastAPI
from endpointTasks.load_data import LoadData

app = FastAPI()

@app.post("/load/")
def load_data(json_file: str, table_id: str):
    LoadData.load_data(json_file, table_id)

@app.post("/preprocess/")
def preprocess_data():
    return {"Hello": "World"}

@app.post("/retrain/")
def detect_mention():
    return {"Probabilities populated": "True"}

@app.post("/infere/")
def detect_mention():
    return {"Probabilities populated": "True"}

@app.post("/notify/")
def detect_mention():
    return {"Probabilities populated": "True"}

if __name__ == '__main__':

    app.run(debug=False, host='0.0.0.0')
