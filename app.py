import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Core Logic Functions

def calculate_payment(principal, annual_rate, years, periods_per_year):
    """Calculates the amortized periodic payment."""
    if annual_rate == 0:
        return principal / (years * periods_per_year)
    
    i = (annual_rate / 100) / periods_per_year
    n = int(years * periods_per_year)
    
    payment = principal * (i * (1 + i)**n) / ((1 + i)**n - 1)
    return payment

def generate_schedule(principal, annual_rate, years, periods_per_year):
    """Generates the full amortization schedule DataFrame."""
    n = int(years * periods_per_year)
    
    if annual_rate == 0:
        payment = principal / n
        i = 0
    else:
        i = (annual_rate / 100) / periods_per_year
        payment = principal * (i * (1 + i)**n) / ((1 + i)**n - 1)
        
    schedule_data = []
    current_balance = principal
    
    for period in range(1, n + 1):
        interest_payment = current_balance * i
        principal_payment = payment - interest_payment
        current_balance -= principal_payment
        current_balance = max(0, current_balance) # Prevent negative balance
        
        schedule_data.append({
            'Period': period,
            'Total Payment': payment,
            'Principal Paid': principal_payment,
            'Interest Paid': interest_payment,
            'Remaining Balance': current_balance
        })
        
    return pd.DataFrame(schedule_data).round(2)

#CSS

def inject_custom_css():
    st.markdown("""
        <style>
        
        .stApp {
            background-color: #0B0E14;
            color: #E0E6ED;
        }
        
        
        div[data-testid="stMetric"] {
            background-color: #151A23;
            border-left: 4px solid #00FF7F;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        }
        
        
        div[data-testid="stMetricValue"] {
            color: #00FF7F;
            font-size: 24px;
            font-weight: 700;
        }
        
        
        .stDownloadButton > button {
            background-color: #00FF7F;
            color: #0B0E14;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stDownloadButton > button:hover {
            background-color: #00CC66;
            color: white;
            border-color: #00CC66;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #11151C;
        }
        </style>
    """, unsafe_allow_html=True)

# Streamlit Web App Interface 

def main():
    st.set_page_config(page_title="Debt Repayment Planner", layout="wide", page_icon="💸")
    

    inject_custom_css()
    
    st.title("💸 Debt Repayment Planner")
    st.markdown("Take control of your loans. Adjust your terms below to generate a dynamic repayment schedule.")

    # Sidebar for Inputs
    st.sidebar.header("⚙️ Loan Details")
    principal = st.sidebar.number_input("Amount Owed (₦)", min_value=1000.0, value=500000.0, step=10000.0)
    annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.0, value=15.0, step=0.1)
    years = st.sidebar.number_input("Time to Repay (Years)", min_value=0.1, value=2.5, step=0.5)

    plan_options = {
        "Yearly": 1,
        "Monthly": 12,
        "Weekly": 52,
        "Daily": 365
    }
    

    unit_labels = {
        "Yearly": "Yrs",
        "Monthly": "Mos",
        "Weekly": "Wks",
        "Daily": "Days"
    }

    st.subheader("1. Repayment Plan Projections")
    
    
    cols = st.columns(4)
    for idx, (plan_name, periods) in enumerate(plan_options.items()):
        total_periods = int(years * periods)
        payment = calculate_payment(principal, annual_rate, years, periods)
        
    
        label_with_freq = f"{plan_name} ({total_periods} {unit_labels[plan_name]})"
        cols[idx].metric(label=label_with_freq, value=f"₦{payment:,.2f}")

    st.markdown("---")

    
    st.subheader("2. Analyze Your Plan")
    selected_plan = st.selectbox("Select a frequency to view the full amortization schedule:", list(plan_options.keys()))
    periods_per_year = plan_options[selected_plan]
    
    df = generate_schedule(principal, annual_rate, years, periods_per_year)
    
    total_paid = df['Total Payment'].sum()
    total_interest = df['Interest Paid'].sum()
    
   
    tot_col1, tot_col2 = st.columns(2)
    tot_col1.metric("Total Amount to be Paid", f"₦{total_paid:,.2f}")
    tot_col2.metric("Total Interest Paid", f"₦{total_interest:,.2f}")

    
    st.subheader("3. Principal vs. Interest Over Time")
    
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 4))
    
    
    fig.patch.set_facecolor('#0B0E14')
    ax.set_facecolor('#0B0E14')
    
    
    ax.plot(df['Period'], df['Principal Paid'], label='Principal Paid', color='#00FF7F', linewidth=2.5) # Neon Green
    ax.plot(df['Period'], df['Interest Paid'], label='Interest Paid', color='#FF4B4B', linewidth=2.5) # Neon Red
    
    ax.set_xlabel(f'Time ({selected_plan} Periods)', color='#E0E6ED')
    ax.set_ylabel('Amount (₦)', color='#E0E6ED')
    
    
    ax.grid(True, linestyle='--', alpha=0.2, color='#E0E6ED')
    for spine in ax.spines.values():
        spine.set_color('#333333')
        
    ax.legend(facecolor='#151A23', edgecolor='#333333')
    
    st.pyplot(fig)

    
    st.subheader("4. Amortization Schedule")
    
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Schedule as CSV",
        data=csv,
        file_name='amortization_schedule.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()