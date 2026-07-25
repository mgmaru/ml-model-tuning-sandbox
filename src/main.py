import streamlit as st

def main():

    top_page = st.Page(
        page="contents/data_page.py", title="Data", default=True
    )
    prediction = st.Page(
        page="contents/prediction_page.py", title="Prediction"
    )

    pg = st.navigation([top_page, prediction])
    pg.run()

if __name__ == "__main__":
    main()
