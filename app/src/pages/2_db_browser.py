import streamlit as st
import pandas as pd
import json
from utils.helpers import get_connection
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils.auth_wrapper import require_auth
import traceback

@require_auth
def main():
    st.title("Browse Metrics Database")

    conn = get_connection()
    cursor = conn.cursor()

    # Get all data
    cursor.execute("SELECT date, org, data FROM metrics ORDER BY date DESC")
    rows = cursor.fetchall()
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=['Date', 'Organization', 'Data'])
    
    if df.empty:
        st.info("No data found in the database.")
        conn.close()
        return
        
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
    filtered_df = df[mask].copy()  # Create a copy to ensure it's a standalone DataFrame

    # Create a display version of the DataFrame without the Data column
    display_df = filtered_df.copy()
    display_df = display_df.drop('Data', axis=1)
    display_df = display_df.reset_index(drop=True)  # Reset index and drop the old one
    display_df['ID'] = display_df.index  # Add explicit ID column based on new index

    # Store the filtered data in session state for later retrieval
    data_dict = {}
    for i, row in display_df.iterrows():
        index = int(row['ID'])
        data_dict[index] = {
            'Date': filtered_df.iloc[i]['Date'],
            'Organization': filtered_df.iloc[i]['Organization'],
            'Data': filtered_df.iloc[i]['Data']
        }
    st.session_state['filtered_data'] = data_dict
    
    # Configure AgGrid for single row selection
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_grid_options(suppressRowClickSelection=False)
    grid_options = gb.build()
    
    # Display the grid
    grid_response = AgGrid(
        display_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit",
        height=400,
        fit_columns_on_grid_load=True
    )

    # Show EXTENDED debug info (can be removed later)
    with st.sidebar.expander("Debug Info", expanded=False):
        st.write("Grid response type:", type(grid_response))
        st.write("Grid response keys:", grid_response.keys() if isinstance(grid_response, dict) else "Not a dict")
        selected_rows_value = grid_response.get('selected_rows', None)
        st.write("Selected rows type:", type(selected_rows_value))
        st.write("Selected rows value:", selected_rows_value)
        
        # Safely check if we have selected rows
        if (selected_rows_value is not None and 
            isinstance(selected_rows_value, list) and 
            len(selected_rows_value) > 0):
            
            st.write("First selected row:", selected_rows_value[0])
            st.write("Row ID:", selected_rows_value[0].get('ID'))
            row_id = selected_rows_value[0].get('ID')
            st.write("Row ID in filtered_data:", row_id in st.session_state['filtered_data'])
            st.write("Available keys in filtered_data:", list(st.session_state['filtered_data'].keys()))
            
            if row_id in st.session_state['filtered_data']:
                row_data = st.session_state['filtered_data'][row_id]
                st.write("Row data:", row_data)
    
    # Handle row selection - using a safer approach
    selected_rows = grid_response.get('selected_rows', [])
    
    # Safe check for selection
    if selected_rows is not None and len(selected_rows) > 0:
        # Make sure we safely extract the selected row
        if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
            selected_row = selected_rows.iloc[0].to_dict()
        elif isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_row = selected_rows[0]
        else:
            st.warning("Could not retrieve selected row data")
            return
        if isinstance(selected_row, dict) and 'ID' in selected_row:
            row_id = int(selected_row.get('ID', -1))
            
            # Extra debug
            st.sidebar.write(f"Selected row ID: {row_id}")
            
            if row_id in st.session_state['filtered_data']:
                row_data = st.session_state['filtered_data'][row_id]
                
                # Extra debug
                st.sidebar.write(f"Found row data: {type(row_data)}")
                
                # Safely get the data field
                data_field = row_data.get('Data', 'Not found')
                if data_field != 'Not found':
                    st.sidebar.write(f"Data field preview: {data_field[:30]}...")
                    
                    try:
                        json_data = json.loads(data_field)
                        
                        # Extra debug
                        st.sidebar.write(f"JSON parsed successfully")
                        
                        # Display the details
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
                    except json.JSONDecodeError as e:
                        st.error(f"Could not parse JSON data: {e}")
                        st.sidebar.code(data_field[:100])
                    except Exception as e:
                        st.error(f"Error processing data: {type(e).__name__}: {str(e)}")
                        st.sidebar.code(traceback.format_exc())
                else:
                    st.error("No data field found in the selected row")
            else:
                st.error(f"Row with ID {row_id} not found in data. Available IDs: {list(st.session_state['filtered_data'].keys())}")
        else:
            st.error("Selected row does not contain an ID field")
    else:
        st.info("Select a row to view its details")

    conn.close()

if __name__ == "__main__":
    main()