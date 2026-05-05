import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

user_input = [-1,1,1,1,-1,-1,-1,-1,-1,1,1,-1,1,-1,1,-1,-1,-1,0,1,1,1,1,-1,-1,-1,-1,1,1,-1]  
model = joblib.load("best_model.pkl")
scaler = joblib.load("standard_scaler.pkl")

user_input_np = np.array(user_input).reshape(1, -1)
user_input_scaled = scaler.transform(user_input_np)

prediction = model.predict(user_input_scaled)[0]

if prediction == 1:
    print("The website is LEGITIMATE.")
else:
    print("WARNING: The website is likely a PHISHING attempt!")