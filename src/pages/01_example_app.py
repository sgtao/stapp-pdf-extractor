# 01_example_app.py
import streamlit as st

from logic.calculations import calculate_spiral
from ui.spiral_chart import spiral_chart

# # メインページに移動
# st.page_link("main.py", label="Go to Main", icon="🏠")

st.title("Streamlit Example App")

"""
In the meantime,
below is an example of what you can do with just a few lines of code:
"""

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

# calculate axises and indices
x, y, indices = calculate_spiral(num_points, num_turns)

# plot chart
spiral_chart(x, y, indices, num_points)
