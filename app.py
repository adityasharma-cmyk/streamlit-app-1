import streamlit as st
import pandas as pd
import numpy as np
import json
from ast import literal_eval
from openai import OpenAI
import importlib

# ---------------------------
# Setup OpenAI client
# ---------------------------
client = OpenAI(
    api_key="sk-VcENPSfApQsYV_mIxTWAFg",  # replace with your key
    base_url="https://imllm.intermesh.net/v1"  # custom endpoint
)

# ---------------------------
# Load static Excel file
# ---------------------------
excel_path = "test file open ai.xlsx"   # <-- put your file path here

# Read multiple sheets
df_disbursed = pd.read_excel(excel_path, sheet_name="disbursed cases")
df_loans = pd.read_excel(excel_path, sheet_name="all loans")

# ---------------------------
# Describe schema
# ---------------------------
data_description = """
We have 2 DataFrames:

1. df_disbursed: this contains details of seller loan disbursed through us, like amount, monthly emi payment delays,open date, close date etc.
Following are the columns: 
- Seller Id
- Jul-25 (no of days past due (DPD) in Jul-25)
- Jun-25 (no of days past due (DPD) in Jun-25)
- May-25 (no of days past due (DPD) in May-25)
- Apr-25 (no of days past due (DPD) in Apr-25)
- Mar-25 (no of days past due (DPD) in Mar-25)
- Feb-25 (no of days past due (DPD) in Feb-25)
- Jan-25 (no of days past due (DPD) in Jan-25)
- Dec-24 (no of days past due (DPD) in Dec-24)
- Nov-24 (no of days past due (DPD) in Nov-24)
- Oct-24 (no of days past due (DPD) in Oct-24)
- Sep-24 (no of days past due (DPD) in Sep-24)
- Aug-24 (no of days past due (DPD) in Aug-24)
- Jul-24 (no of days past due (DPD) in Jul-24)
- Jun-24 (no of days past due (DPD) in Jun-24)
- May-24 (no of days past due (DPD) in May-24)
- Apr-24 (no of days past due (DPD) in Apr-24)
- Mar-24 (no of days past due (DPD) in Mar-24)
- Feb-24 (no of days past due (DPD) in Feb-24)
- Jan-24 (no of days past due (DPD) in Jan-24)
- Dec-23 (no of days past due (DPD) in Dec-23)
- Nov-23 (no of days past due (DPD) in Nov-23)
- Oct-23 (no of days past due (DPD) in Oct-23)
- Sep-23 (no of days past due (DPD) in Sep-23)
- Aug-23 (no of days past due (DPD) in Aug-23)
- Jul-23 (no of days past due (DPD) in Jul-23)
- Jun-23 (no of days past due (DPD) in Jun-23)
- May-23 (no of days past due (DPD) in May-23)
- Apr-23 (no of days past due (DPD) in Apr-23)
- Mar-23 (no of days past due (DPD) in Mar-23)
- Feb-23 (no of days past due (DPD) in Feb-23)
- Jan-23 (no of days past due (DPD) in Jan-23)
- Open Date (Open date of tradeline)
- Close Date
- Disbursed Amount
- Outstanding Amount
- SuitFiled_WillfulDefault (1 if SuitFiled_WillfulDefault)
- Written_off_Settled_Status (1 if Written_off or Settled)
- Written_Off_Amt_Total
- Rate_of_Interest (roi as per scrub. is number indicating percetage)
- AccountHoldertypeCode
- Current Custtype (current service type of seller)
- Lender
- Service Type during application
- ROI (roi as per us. In percentage)
- Paid Vintage (number)
Note that use ROI (as per us) by default. Also note that use this dataframe when asked about details of loans disbursed through us/hellotrade/Indiamart

2. df_loans: This contains details of all loans of the sellers in df_disbursed. All loans means loansvdisbursed through us or through any other institution.
Following are the columns:  
- Seller Id: also present in df_disbursed (this is the matching key between both dataframes)
- Institute Type: lender type or type of institute through which tradeline was opened like NBF for NBFC, PUB for public sector bank, PVT for private sector bank etc
- Account type: Type of loan
- Open date: Open date of tradeline
- Sanction Amount: Disbursed Amount
- Terms_Duration: Tenure of loan
- Terms_Frequency: Tenure of loan measured in. For ex: 'M' for monthly , 'Q' for quarterly , 'F' for biweekly
- Current_Balance: outstanding amount
- Amount_Past_Due: 
- Date Closed: closed date of tradeline. Blank or null means tradeline is still open
- SuitFiledWillfulDefaultWrittenOffStatus: 
- SuitFiled_WillfulDefault: 
- Written_off_Settled_Status: 2 or 4 means 'written off' , 3 means 'settled' . use this col for written off/settled.
- Settlement_Amount: 
- Value_of_Collateral: 
- Written_Off_Amt_Total: 
- Written_Off_Amt_Principal: 
- Rate_of_Interest: roi as per scrub. is number indicating percetage
- Repayment_Tenure: 
- AccountHoldertypeCode: 
- CAIS_Account_History: in this format: [{'Year': '2023', 'Month': '09', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '08', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '07', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '06', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '05', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '04', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '03', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '02', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2023', 'Month': '01', 'Days_Past_Due': '0', 'Asset_Classification': '?'}, {'Year': '2022', 'Month': '12', 'Days_Past_Due': '0', 'Asset_Classification': '?'}]
- Account_Review_Data: in this format: [{'Year': '2023', 'Month': '9', 'Account_Status': '13', 'Actual_Payment_Amount': '104428', 'Current_Balance': '0', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '8', 'Account_Status': '11', 'Actual_Payment_Amount': '104428', 'Current_Balance': '56059', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '7', 'Account_Status': '11', 'Actual_Payment_Amount': '36396', 'Current_Balance': '60691', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '6', 'Account_Status': '11', 'Actual_Payment_Amount': '30802', 'Current_Balance': '65250', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '5', 'Account_Status': '11', 'Actual_Payment_Amount': '25208', 'Current_Balance': '69738', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '4', 'Account_Status': '11', 'Actual_Payment_Amount': '18670', 'Current_Balance': '74156', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '3', 'Account_Status': '11', 'Actual_Payment_Amount': '12604', 'Current_Balance': '78505', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '2', 'Account_Status': '11', 'Actual_Payment_Amount': '6538', 'Current_Balance': '82786', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2023', 'Month': '1', 'Account_Status': '11', 'Actual_Payment_Amount': '', 'Current_Balance': '87000', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}, {'Year': '2022', 'Month': '12', 'Account_Status': '11', 'Actual_Payment_Amount': '', 'Current_Balance': '87000', 'Credit_Limit_Amount': '87000', 'Amount_Past_Due': '0', 'Cash_Limit': '', 'EMI_Amount': '5594'}]
Note that use this dataframe when asked about other loans or open market loans or all loans of sellers in df_disbursed.
Also dont show index colum in the output data.
"""

# ---------------------------
# Auto-import helper
# ---------------------------
def auto_import(extra_globals=None):
    imports = {
        "pd": "pandas",
        "np": "numpy",
        "json": "json",
        "literal_eval": "ast.literal_eval"
    }
    exec_env = extra_globals.copy() if extra_globals else {}
    for alias, lib in imports.items():
        try:
            exec_env[alias] = importlib.import_module(lib)
        except Exception:
            pass
    return exec_env

# ---------------------------
# Custom CSS to widen sidebar
# ---------------------------
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 320px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 80px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Streamlit UI
# ---------------------------
col1, col2 = st.columns([1, 5])

with col1:
    st.image("logo.png", width=120)

with col2:
    st.markdown("<h1 style='margin-top: -10px;'>Portfolio Chatbot</h1>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------
# Sidebar (clean description)
# ---------------------------
st.sidebar.title("📘 About This Chatbot")
st.sidebar.markdown("""
This chatbot helps you ask questions about **HelloTrade portfolio data** as well as **loan data from the open market** for these sellers.  

It contains details such as:  
- Loan disbursement amounts and dates  
- Current and outstanding balances  
- Overdues or delays (DPD)  
- Written off or settled status  
- Lender names of HelloTrade disbursed cases  
- Loan Types of open market loans
- Service type of each seller  
- Lender type (Private, Public, NBFC), etc.

You can ask questions like:  
> • what is the disbursed and outstanding amount of our portfolio? 
> • Pivot of lender name in rows and disbursed amount bucket in cols. disbursed amount bucket to be used: <1L, 1L-5L,5L-10L>10L? 
> • In rows custtype of sellers, in cols: count of unique sellers with dpd>0,dpd>30,dpd>60,dpd>90 in any month?
> • output details of all market loans of sellers with dpd>90 in our portfolio. details should include seller id, loan type, amount, month wise dpd, open date, close date, roi?

""")

st.sidebar.markdown("---")


query = st.text_input("Ask me something about the Portfolio:")

if query:
    st.write("### 🔍 Your Query:")
    st.write(query)

    prompt = f"""
You are a Python data assistant.
You have these pandas DataFrames already loaded:

{data_description}

Treat all empty values as 0 if column is numeric.
Generate valid pandas code using these DataFrames.
You already have access to these modules: 
- pandas as pd
- numpy as np
- json
- ast.literal_eval

⚠️ You may write import statements if needed.
Always assign the final answer to a variable named result.
Only return code, no explanations, no markdown.

User query: {query}
"""

    try:
        response = client.chat.completions.create(
            model="google/gemini-2.5-pro",
            messages=[{"role": "user", "content": prompt}]
        )

        code = response.choices[0].message.content.strip()
        code = code.replace("```python", "").replace("```", "").strip()

        #st.code(code, language="python")

        # ---------------------------
        # Prepare environment with auto imports
        # ---------------------------
        extra_globals = {
            "df_disbursed": df_disbursed,
            "df_loans": df_loans
        }
        exec_env = auto_import(extra_globals=extra_globals)

        # ---------------------------
        # Execute generated code
        # ---------------------------
        exec(code, exec_env)

        if "result" in exec_env:
            result = exec_env["result"]

            if isinstance(result, pd.DataFrame):
                st.write("### ✅ Result:")
                st.dataframe(result)
            else:
                st.write("### ✅ Result:")
                st.write(result)
        else:
            st.error("⚠️ No 'result' variable found in code output.")

    except Exception as e:
        st.error(f"⚠️ Error executing code: {e}")
