# spiral_chart.py
import altair as alt
import pandas as pd
import streamlit as st
import numpy as np


def spiral_chart(x, y, indices, num_points):
    df = pd.DataFrame(
        {
            "x": x,
            "y": y,
            "idx": indices,
            "rand": np.random.randn(num_points),
        }
    )

    chart = (
        alt.Chart(df, height=700, width=700)
        .mark_point(filled=True)
        .encode(
            x=alt.X("x", axis=None),
            y=alt.Y("y", axis=None),
            color=alt.Color("idx", legend=None, scale=alt.Scale()),
            size=alt.Size(
                "rand", legend=None, scale=alt.Scale(range=[1, 150])
            ),
        )
    )

    st.altair_chart(chart)
