from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from Users.models import Prediction
from django.db.models import Count
from collections import Counter
import json

import pandas as pd
import joblib
from django.core.files.storage import default_storage
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

def adminhome(request):
    users = User.objects.filter(is_staff=False, is_superuser=False) 
    return render(request, "Admin/adminhome.html", {"users": users})

def admin_update_userstatus(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        if user.is_active:
            messages.success(request, f"User {user.username} has been activated.")
        else:
            messages.success(request, f"User {user.username} has been deactivated.")
        
        return redirect('adminhome')  
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('adminhome')


def adminuserratio(request):
    predictions = Prediction.objects.all()
    data = Counter(p.prediction_result for p in predictions)

    legit_count = data.get('LEGITIMATE', 0)
    phishing_count = data.get('PHISHING', 0)

    chart_data = {
        'labels': ['LEGITIMATE', 'PHISHING'],
        'values': [legit_count, phishing_count]
    }

    return render(request, 'Admin/adminuserprediction.html', {
        'chart_data': json.dumps(chart_data)
    })

def admin_accuracy(request):
    accuracy_results = None

    if request.method == 'POST' and request.FILES.get('dataset'):
        file = request.FILES['dataset']
        file_path = default_storage.save('tmp/' + file.name, file)

        try:

            df = pd.read_csv(default_storage.path(file_path))

            if 'key' in df.columns:
                df.drop('key', axis=1, inplace=True)

            df['Result'] = df['Result'].replace(-1, 0)
            X = df.drop('Result', axis=1)
            y = df['Result'].astype(int)

            # Train/Test Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )

            # Scale
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            joblib.dump(scaler, 'standard_scaler.pkl')

            # Logistic Regression
            lr = LogisticRegression(max_iter=1000)
            lr.fit(X_train_scaled, y_train)
            acc_lr_train = lr.score(X_train_scaled, y_train) * 100
            acc_lr_test = accuracy_score(y_test, lr.predict(X_test_scaled)) * 100

            # Random Forest
            rf = RandomForestClassifier()
            rf.fit(X_train_scaled, y_train)
            acc_rf_train = rf.score(X_train_scaled, y_train) * 100
            acc_rf_test = accuracy_score(y_test, rf.predict(X_test_scaled)) * 100

            # XGBoost
            xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
            xgb.fit(X_train_scaled, y_train)
            acc_xgb_train = xgb.score(X_train_scaled, y_train) * 100
            acc_xgb_test = accuracy_score(y_test, xgb.predict(X_test_scaled)) * 100

            best_model = max(
                [('logistic_regression', acc_lr_test, lr),
                 ('random_forest', acc_rf_test, rf),
                 ('xgboost', acc_xgb_test, xgb)],
                key=lambda x: x[1]
            )

            joblib.dump(best_model[2], 'best_model.pkl')
            accuracy_results = [
                {'model': 'Logistic Regression', 'train': acc_lr_train, 'test': acc_lr_test},
                {'model': 'Random Forest', 'train': acc_rf_train, 'test': acc_rf_test},
                {'model': 'XGBoost', 'train': acc_xgb_train, 'test': acc_xgb_test},
                {'model': 'Best Model Saved', 'train': '-', 'test': best_model[0].upper()},
            ]

        except Exception as e:
            accuracy_results = [{'model': 'Error', 'train': '-', 'test': str(e)}]

    return render(request, 'Admin/adminaccuracy.html', {
        'accuracy_results': accuracy_results
    })