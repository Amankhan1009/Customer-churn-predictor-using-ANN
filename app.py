import streamlit as st
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
import pandas as pd
import pickle

# Set page config
st.set_page_config(page_title='Customer Churn Predictor', layout='centered', page_icon='📉')

# Load the trained model
model = tf.keras.models.load_model('model.h5')

# Load the encoders and scaler
with open('label_encoder_gender.pkl', 'rb') as file:
    label_encoder_gender = pickle.load(file)

with open('onehot_encoder_geo.pkl', 'rb') as file:
    onehot_encoder_geo = pickle.load(file)

with open('scaler.pkl', 'rb') as file:
    scaler = pickle.load(file)

# App title
st.title('📉 Customer Churn Prediction')
st.markdown("Use this tool to predict the likelihood of a customer churning based on their profile.")

st.header("📝 Enter Customer Information")

# Create input layout
col1, col2 = st.columns(2)

with col1:
    geography = st.selectbox('🌍 Geography', onehot_encoder_geo.categories_[0])
    gender = st.selectbox('👤 Gender', label_encoder_gender.classes_)
    age = st.slider('🎂 Age', 18, 92)
    credit_score = st.number_input('💳 Credit Score', min_value=300, max_value=900, step=1)
    balance = st.number_input('💰 Balance')

with col2:
    estimated_salary = st.number_input('💼 Estimated Salary')
    tenure = st.slider('📆 Tenure (Years)', 0, 10)
    num_of_products = st.slider('📦 Number of Products', 1, 4)
    has_cr_card = st.radio('💳 Has Credit Card', [0, 1], format_func=lambda x: 'Yes' if x else 'No')
    is_active_member = st.radio('✅ Is Active Member', [0, 1], format_func=lambda x: 'Yes' if x else 'No')

# Submit button
if st.button('🔍 Predict Churn'):
    # Prepare input data
    input_data = pd.DataFrame({
        'CreditScore': [credit_score],
        'Gender': [label_encoder_gender.transform([gender])[0]],
        'Age': [age],
        'Tenure': [tenure],
        'Balance': [balance],
        'NumOfProducts': [num_of_products],
        'HasCrCard': [has_cr_card],
        'IsActiveMember': [is_active_member],
        'EstimatedSalary': [estimated_salary]
    })

    # One-hot encode 'Geography'
    geo_encoded = onehot_encoder_geo.transform([[geography]]).toarray()
    geo_encoded_df = pd.DataFrame(geo_encoded, columns=onehot_encoder_geo.get_feature_names_out(['Geography']))

    # Combine encoded data
    input_data = pd.concat([input_data.reset_index(drop=True), geo_encoded_df], axis=1)

    # Scale the input
    input_data_scaled = scaler.transform(input_data)

    # Predict churn
    prediction = model.predict(input_data_scaled)
    prediction_proba = prediction[0][0]

    # Display result
    st.subheader("📊 Prediction Result")
    st.metric(label="Churn Probability", value=f"{prediction_proba:.2%}")

    if prediction_proba > 0.5:
        st.error("🚨 The customer is likely to **churn**.")
    else:
        st.success("✅ The customer is **not likely** to churn.")
