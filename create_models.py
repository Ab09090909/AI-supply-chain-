"""
Model Generation Script
Creates dummy ML models for demonstration
"""
import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LinearRegression

def create_models():
    """Generate all required ML models"""
    os.makedirs("models", exist_ok=True)
    
    print("Creating ML models...")
    
    # 1. Fraud Detection Model
    print("  - Fraud detection model...")
    fraud_model = RandomForestClassifier(n_estimators=100, random_state=42)
    X_fraud = np.random.rand(1000, 8)
    y_fraud = np.random.randint(0, 2, 1000)
    fraud_model.fit(X_fraud, y_fraud)
    with open("models/fraud_model.pkl", "wb") as f:
        pickle.dump(fraud_model, f)
    
    # 2. Merchant Matching Model
    print("  - Merchant matching model...")
    matching_model = NearestNeighbors(n_neighbors=5)
    X_match = np.random.rand(500, 5)
    matching_model.fit(X_match)
    with open("models/matching_model.pkl", "wb") as f:
        pickle.dump(matching_model, f)
    
    # 3. Price Prediction Model
    print("  - Price prediction model...")
    price_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    X_price = np.random.rand(1000, 3)
    y_price = np.random.rand(1000) * 100
    price_model.fit(X_price, y_price)
    with open("models/price_model.pkl", "wb") as f:
        pickle.dump(price_model, f)
    
    # 4. Demand Forecast Model
    print("  - Demand forecast model...")
    demand_model = LinearRegression()
    X_demand = np.random.rand(1000, 5)
    y_demand = np.random.rand(1000) * 1000
    demand_model.fit(X_demand, y_demand)
    with open("models/demand_model.pkl", "wb") as f:
        pickle.dump(demand_model, f)
    
    # 5. Recommendation Model
    print("  - Recommendation model...")
    from sklearn.decomposition import NMF
    rec_model = NMF(n_components=3, random_state=42)
    X_rec = np.random.rand(100, 10)
    rec_model.fit(X_rec)
    with open("models/recommendation_model.pkl", "wb") as f:
        pickle.dump(rec_model, f)
    
    print("✅ All models created successfully in /models/")
    print("   - fraud_model.pkl")
    print("   - matching_model.pkl")
    print("   - price_model.pkl")
    print("   - demand_model.pkl")
    print("   - recommendation_model.pkl")

if __name__ == "__main__":
    create_models()
