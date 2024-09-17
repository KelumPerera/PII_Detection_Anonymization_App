# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 18:24:57 2024

@author: Kelum.Perera
"""

import base64
from io import BytesIO
import streamlit as st
import pandas as pd
from openpyxl import Workbook
from presidio_analyzer import AnalyzerEngine

# Initialize the AnalyzerEngine
analyzer = AnalyzerEngine()

# Function to detect PII in a text string and replace it with asterisks
def detect_and_replace_pii(text):
    analysis_results = analyzer.analyze(text=text, language='en')
    # Filter out URL results
    analysis_results = [result for result in analysis_results if result.entity_type != 'URL']
    text_modified = text
    offset = 0
    for result in analysis_results:
        # Calculate the replacement text
        replacement = '*' * (result.end - result.start)
        # Replace the PII text with asterisks
        text_modified = text_modified[:result.start + offset] + replacement + text_modified[result.end + offset:]
        # Update the offset due to text modifications
        offset += len(replacement) - (result.end - result.start)
    return text_modified

# Function to convert DataFrame to Excel and create download link
def df_to_excel_download_link(df, filename):
    try:
        output = BytesIO()
        
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Sheet1'

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            writer.book = workbook
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
             
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel file</a>'

        return href
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def main():
    # Google Analytics tracking
    st.markdown("""
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXXX-X"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'UA-XXXXXX-X');
        </script>
        """, unsafe_allow_html=True)
        
    st.title('PII Detection and Anonymization Application')

    st.markdown("""
                
        This application uses the **Microsoft Presidio** library to detect and anonymize personally identifiable information (PII). 
        Presidio is an open-source data protection and anonymization API developed by Microsoft, which helps in identifying and masking PII data.
        For more information, visit the [Presidio GitHub repository](https://github.com/microsoft/presidio).
    """)

    # User input options: Text Input or File Upload
    input_method = st.radio("Choose input method:", ('Free Text', 'Upload File'))

    if input_method == 'Free Text':
        # Free text input
        user_text = st.text_area("Enter your text:", height=300)
        if st.button('Detect and Replace PII in Text'):
            if user_text:
                # Convert text to DataFrame
                df = pd.DataFrame([user_text], columns=['text'])
                df['text'] = df['text'].apply(detect_and_replace_pii)
                st.write("Data with PII redacted:")
                st.dataframe(df)
                st.markdown(df_to_excel_download_link(df, 'redacted_text.xlsx'), unsafe_allow_html=True)
            else:
                st.warning("Please enter some text.")

    elif input_method == 'Upload File':
        # File uploader
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'csv', 'xlsx'])

        if uploaded_file is not None:
            try:
                # Read the file into a DataFrame
                if uploaded_file.type == "text/csv":
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    df = pd.read_excel(uploaded_file, engine='openpyxl')
                else:
                    st.error("Unsupported file type.")
                    return

                # Display the DataFrame
                st.write("Data from file:")
                st.dataframe(df)

                # Button to detect and replace PII
                if st.button('Detect and Replace PII in File'):
                    # Apply PII detection to each text column
                    for col in df.columns:
                        if df[col].dtype == object:  # Check for text columns
                            df[col] = df[col].apply(detect_and_replace_pii)
                    st.write("Data with PII redacted:")
                    st.dataframe(df)
                    st.markdown(df_to_excel_download_link(df, 'redacted_data.xlsx'), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error processing file: {e}")
    # Add a footer
    st.markdown("""
    <hr>
    <p class="footer">Developed by Kelum Perera, Data Privacy Auditor, Chartered Accountant, LLB (Hons), C|HFI, AWS Certified Solution Architect.</p>
    """, unsafe_allow_html=True)
        

# Custom styling
st.markdown("""
    <style>
    .reportview-container {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    .Widget>label {
        color: brown;
        font-family: monospace;
    }
    [class^="st-b"]  {
        color: brown;
        font-family: monospace;
    }
    .st-at {
        background-color: rgba(255, 255, 255, 0.8);
    }
    .footer {
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
