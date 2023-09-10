import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def generate_agrid(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gridoptions = gb.build()

    grid_response = AgGrid(
        df,
        height=200,
        gridOptions=gridoptions,
        update_mode=GridUpdateMode.MANUAL
    )
    selected = grid_response['selected_rows']

    # Show the selected row.
    if selected:
        st.write('selected')
        st.dataframe(selected)

    return grid_response


def add_row(grid_table):
    df = pd.DataFrame(grid_table['data'])

    new_row = [['', 100]]
    df_empty = pd.DataFrame(new_row, columns=df.columns)
    df = pd.concat([df, df_empty], axis=0, ignore_index=True)

    # Save new df to sample.csv.
    df.to_csv('C:/Users/JiaPeng/Desktop/test/sample.csv', index=False)


def get_data():
    """Reads sample.csv and return a dataframe."""
    return pd.read_csv('C:/Users/JiaPeng/Desktop/test/sample.csv')


if __name__ == '__main__':
    df = get_data()
    grid_response = generate_agrid(df)

    st.sidebar.button("Add row", on_click=add_row, args=[grid_response])