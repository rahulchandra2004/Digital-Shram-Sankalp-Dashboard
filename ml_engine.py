import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, HistGradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler

def detect_anomalies(df):
    """
    Tri-Modal AI Engine:
    1. Statistical: Isolation Forest
    2. Deep Learning: Autoencoder (Simulated via MLPRegressor)
    3. Forecasting: LSTM (Simulated via HistGradientBoostingRegressor on time-series aggregates)
    """
    df_ml = df.copy()
    
    # Label encoding
    le_state = LabelEncoder()
    df_ml['State_Origin_Encoded'] = le_state.fit_transform(df_ml['State_Origin'])
    df_ml['State_Current_Encoded'] = le_state.fit_transform(df_ml['State_Current'])
    
    le_sector = LabelEncoder()
    df_ml['Sector_Encoded'] = le_sector.fit_transform(df_ml['Occupation_Sector'])
    
    le_skill = LabelEncoder()
    df_ml['Skill_Encoded'] = le_skill.fit_transform(df_ml['Skill_Level'])
    
    # Features for Anomaly models
    features = ['Age', 'Daily_Wage', 'State_Origin_Encoded', 'State_Current_Encoded', 'Sector_Encoded', 'Skill_Encoded']
    X = df_ml[features]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # ---------------------------------------------------------
    # TIER 1: Statistical (Isolation Forest)
    # ---------------------------------------------------------
    iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    stat_predictions = iso_forest.fit_predict(X_scaled)
    df['Is_Anomaly_Stat'] = (stat_predictions == -1)
    
    # ---------------------------------------------------------
    # TIER 2: Deep Learning (Autoencoder via MLP)
    # ---------------------------------------------------------
    autoencoder = MLPRegressor(hidden_layer_sizes=(3,), activation='relu', solver='adam', max_iter=500, random_state=42)
    autoencoder.fit(X_scaled, X_scaled)
    X_pred = autoencoder.predict(X_scaled)
    
    reconstruction_errors = np.mean(np.square(X_scaled - X_pred), axis=1)
    df['DL_Reconstruction_Error'] = reconstruction_errors
    
    threshold_dl = np.percentile(reconstruction_errors, 95)
    df['Is_Anomaly_DL'] = (reconstruction_errors >= threshold_dl)
    
    df['Is_Anomaly'] = df['Is_Anomaly_Stat'] | df['Is_Anomaly_DL']
    
    # ---------------------------------------------------------
    # TIER 3: Explainability (XAI) - Generate Human-Readable Reasons
    # ---------------------------------------------------------
    reasons = []
    for _, row in df.iterrows():
        if not row['Is_Anomaly']:
            reasons.append("Clean")
            continue
            
        row_reasons = []
        if row['Is_Anomaly_DL']:
            row_reasons.append("Complex non-linear profile (Autoencoder mismatch)")
            
        if row['Is_Anomaly_Stat']:
            if row['Daily_Wage'] > 2000 or row['Daily_Wage'] < 50:
                row_reasons.append(f"Extreme Wage Outlier ({row['Daily_Wage']})")
            if row['Age'] < 18 and row['Skill_Level'] == 'Highly-skilled':
                row_reasons.append("Impossible Age-to-Skill ratio")
            if row['Age'] < 0:
                row_reasons.append("Negative Age detected")
            if not row_reasons: # If no specific heuristic caught it, default to generic stat reason
                row_reasons.append("Structural outlier (Isolation Forest)")
                
        reasons.append(" | ".join(row_reasons))
        
    df['Anomaly_Reason'] = reasons
    
    return df

def generate_forecast(df):
    """
    Generates a 6-month migration forecast simulating an LSTM network.
    Groups the data by Registration_Date (Month) and uses historical volume to predict future volume.
    """
    # Create month-year column
    df['Reg_Date'] = pd.to_datetime(df['Registration_Date'])
    df['Month_Year'] = df['Reg_Date'].dt.to_period('M')
    
    # Aggregate migration volume (where Origin != Current)
    mig_df = df[df['State_Origin'] != df['State_Current']]
    monthly_mig = mig_df.groupby('Month_Year').size().reset_index(name='Volume')
    
    # Convert period to timestamp for sorting and processing
    monthly_mig['Month_Year_Ts'] = monthly_mig['Month_Year'].dt.to_timestamp()
    monthly_mig = monthly_mig.sort_values('Month_Year_Ts')
    
    # Create simple autoregressive features (lags)
    monthly_mig['Lag_1'] = monthly_mig['Volume'].shift(1).bfill()
    monthly_mig['Lag_2'] = monthly_mig['Volume'].shift(2).bfill()
    monthly_mig['Month_Num'] = monthly_mig['Month_Year_Ts'].dt.month
    
    # Train forecasting model (Simulating LSTM logic using Gradient Boosting on lags)
    features = ['Lag_1', 'Lag_2', 'Month_Num']
    X = monthly_mig[features]
    y = monthly_mig['Volume']
    
    forecaster = HistGradientBoostingRegressor(random_state=42)
    forecaster.fit(X, y)
    
    # Predict next 6 months
    last_date = monthly_mig['Month_Year_Ts'].max()
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 7)]
    
    future_df = pd.DataFrame({'Month_Year_Ts': future_dates})
    future_df['Month_Num'] = future_df['Month_Year_Ts'].dt.month
    
    # Iterative prediction
    predictions = []
    curr_lag1 = monthly_mig['Volume'].iloc[-1]
    curr_lag2 = monthly_mig['Volume'].iloc[-2]
    
    for _, row in future_df.iterrows():
        pred = forecaster.predict(pd.DataFrame({'Lag_1': [curr_lag1], 'Lag_2': [curr_lag2], 'Month_Num': [row['Month_Num']]}))[0]
        # Add a bit of seasonal noise for realism
        pred = max(50, pred + np.random.normal(0, 20)) 
        predictions.append(int(pred))
        curr_lag2 = curr_lag1
        curr_lag1 = pred
        
    future_df['Predicted_Volume'] = predictions
    future_df['Type'] = 'Forecast'
    
    # Format historical for plotting
    historical = monthly_mig[['Month_Year_Ts', 'Volume']].copy()
    historical = historical.rename(columns={'Volume': 'Predicted_Volume'})
    historical['Type'] = 'Historical'
    
    # Combine
    combined = pd.concat([historical, future_df[['Month_Year_Ts', 'Predicted_Volume', 'Type']]])
    return combined

def run_ml_pipeline(data_path="workers_data.csv"):
    try:
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} records for ML analysis.")
        df_analyzed = detect_anomalies(df)
        forecast_df = generate_forecast(df_analyzed)
        
        num_stat = df_analyzed['Is_Anomaly_Stat'].sum()
        num_dl = df_analyzed['Is_Anomaly_DL'].sum()
        print(f"Detected {num_stat} Stat anomalies, {num_dl} DL anomalies.")
        
        return df_analyzed, forecast_df
    except Exception as e:
        print(f"Error in ML pipeline: {e}")
        return None, None

if __name__ == "__main__":
    run_ml_pipeline()
