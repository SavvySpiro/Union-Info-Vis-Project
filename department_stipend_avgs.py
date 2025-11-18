import pandas as pd
import plotly.express as px
import utils



def department_stipend_avgs():
    """Analyze and visualize department stipend averages over time for Northeastern University."""
    # Load data
    stipends = pd.read_csv("data/boston_stipends.csv")
    
    # Filter for Northeastern University and standardize department names
    neu_mask = stipends["University"] == "Northeastern University"
    stipends.loc[neu_mask, "Department"] = stipends[neu_mask]["Department"].apply(utils.dept_name)
    
    # Calculate department averages by academic year
    neu_stipends = (
        stipends[neu_mask][["Academic Year", "Department", "Overall Pay"]]
        .groupby(["Academic Year", "Department"])
        .mean()
        .reset_index()
    )
    
    # Define departments with sufficient data
    depts_with_data = [
        'computer science', 
        'psychology', 
        'bioengineering', 
        'english',
        'sociology and anthropology', 
        'political science',
        'mechanical and industrial engineering',
        'electrical and computer engineering', 
        'biology', 
        'physics', 
        'history'
    ]
    
    # Filter for departments with data
    neu_avgs = neu_stipends[neu_stipends["Department"].isin(depts_with_data)]
    
    # Create visualization
    neu_stipends_time = px.line(
        neu_avgs,
        x="Academic Year",
        y="Overall Pay",
        color="Department",
        markers=True,
        height=800,
        title="Northeastern University Graduate Stipends by Department Over Time"
    )
    
    # Format y-axis for currency
    neu_stipends_time.update_layout(
        yaxis_tickprefix='$', 
        yaxis_tickformat=',.',
        xaxis_title="Academic Year",
        yaxis_title="Overall Pay (Average)",
        legend_title="Department",
        hovermode='x unified'
    )
    
    
    return neu_stipends_time
