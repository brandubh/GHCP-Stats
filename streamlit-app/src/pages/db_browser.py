import streamlit as st
import pandas as pd
import json
from utils.helpers import get_connection
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def browse_metrics():
    st.title("Browse Metrics Database")

    conn = get_connection()
    cursor = conn.cursor()

    # Get all data
    cursor.execute("SELECT date, org, data FROM metrics ORDER BY date DESC")
    rows = cursor.fetchall()
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=['Date', 'Organization', 'Data'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Add filters in sidebar
    st.sidebar.header("Filters")
    
    # Date range picker
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Organization filter
    orgs = df['Organization'].unique()
    selected_orgs = st.sidebar.multiselect('Select Organizations', orgs, default=orgs)
    
    # Apply filters
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date) & (df['Organization'].isin(selected_orgs))
    filtered_df = df[mask]

    # Create a display version of the DataFrame without the Data column
    display_df = filtered_df.copy()
    display_df = display_df.drop('Data', axis=1)
    display_df = display_df.reset_index()  # Add this line to create a unique index
    display_df = display_df.rename(columns={'index': 'ID'})  # Rename index column

    # Configure AgGrid for single row selection
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_grid_options(suppressRowClickSelection=False)
    gb.configure_column("ID", header_name="ID", hide=True)
    grid_options = gb.build()
    
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit",
        height=400,
        fit_columns_on_grid_load=True
    )

    # Check selected rows properly
    if 'selected_rows' in grid_response and len(grid_response['selected_rows']) > 0:
        selected = grid_response.selected_rows['ID']
        # Use the ID to find the matching row in original DataFrame
        row_data = filtered_df.iloc[selected]
        json_data = json.loads(row_data['Data'].values[0])
        
        with st.expander("JSON Data", expanded=True):
            st.json(json_data)
                
            # Display key metrics
            col1, col2 = st.columns(2)
            with col1:
                if "totalSuggestions" in json_data:
                    st.metric("Total Suggestions", json_data["totalSuggestions"])
            with col2:
                if "acceptanceRate" in json_data:
                    st.metric("Acceptance Rate", f"{json_data['acceptanceRate']}%")
    else:
        st.info("Select a row to view its details")

    conn.close()

if __name__ == "__main__":
    browse_metrics()