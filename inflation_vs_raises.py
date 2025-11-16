import plotly.express as px
import pandas as pd
import numpy as np

# NOTE: DUMMY DATA RN FOR TESTNG
def inflation_vs_raises():
    pathname = "data/cleaned_stipends.csv"
    stipends = pd.read_csv(pathname)