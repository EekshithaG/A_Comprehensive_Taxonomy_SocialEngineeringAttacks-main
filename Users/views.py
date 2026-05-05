from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PredictionForm
from .models import Prediction
import joblib
import numpy as np

# Create your views here.
def userhome(request):
    user = request.user
    return render(request, 'User/userhome.html', {'user':user})

@login_required
def userpredict(request):
    prediction_result = None

    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            input_str = form.cleaned_data['input_data']
            try:
                user_input = list(map(int, input_str.split(',')))

                # Load model and scaler
                model = joblib.load("model/best_model.pkl")
                scaler = joblib.load("model/standard_scaler.pkl")

                user_input_np = np.array(user_input).reshape(1, -1)
                user_input_scaled = scaler.transform(user_input_np)

                prediction = model.predict(user_input_scaled)[0]
                prediction_result = "LEGITIMATE" if prediction == 1 else "PHISHING"

                # Save to DB
                Prediction.objects.create(
                    user=request.user,
                    input_data=input_str,
                    prediction_result=prediction_result
                )

            except Exception as e:
                prediction_result = f"Error in processing input: {str(e)}"

    else:
        form = PredictionForm()

    return render(request, 'User/userpredict.html', {
        'form': form,
        'prediction_result': prediction_result
    })
