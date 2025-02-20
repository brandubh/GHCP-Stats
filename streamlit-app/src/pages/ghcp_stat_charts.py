import streamlit as st
import utils.helpers as helpers
from datetime import date, timedelta, datetime
import pandas as pd
import altair as alt


def page1():
    # Add more components and logic specific to this page here
    # --- Streamlit Frontend ---
    st.title("GitHub Copilot Metrics Dashboard")

    st.header("Metrics Dashboard")

    # Date Range Selector
    today = date.today()
    default_start = today - timedelta(days=7)
    date_range = st.sidebar.date_input("Select Date Range", [default_start, today])
    if len(date_range) != 2:
        st.sidebar.error("Select both start and end dates.")
        st.stop()

    # Organization Selector
    org_options = helpers.get_org_options()
    sel_orgs = st.sidebar.multiselect("Select Organizations", org_options, default=org_options)

    # Load Records
    records = helpers.load_metrics(date_range, sel_orgs)

    # Dynamic Filter Options
    editors_opt, models_opt, languages_opt = helpers.get_filter_options(records)
    sel_editors = st.sidebar.multiselect("Select Editors", editors_opt, default=editors_opt)
    sel_models = st.sidebar.multiselect("Select Models", models_opt, default=models_opt)
    sel_languages = st.sidebar.multiselect("Select Languages", languages_opt, default=languages_opt)

    # Build DataFrame
    df = helpers.build_dataframe(records, sel_editors, sel_models, sel_languages)

    if df.empty:
        st.info("No data available for selected filters.")
    else:
        # Convert date column to datetime if not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter out weekends first
        weekday_mask = df['date'].dt.weekday < 5
        weekday_df = df[weekday_mask]
        
        # Then sum by day for weekdays only
        daily_sums = weekday_df.groupby("date")[["active", "engaged", "inactive"]].sum()
        
        # Calculate averages of daily sums
        st.subheader("Aggregated Metrics (Weekday Averages)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Daily Active Users", round(daily_sums["active"].mean(), 2))
        col2.metric("Avg Daily Engaged Users", round(daily_sums["engaged"].mean(), 2))
        col3.metric("Avg Daily Inactive Users", round(daily_sums["inactive"].mean(), 2))
        
        # Rest of the metrics remain summed (for all days)
        col4, col5, col6 = st.columns(3)
        col4.metric("Total Suggested Lines", int(df["suggested"].sum()))
        col5.metric("Total Accepted Lines", int(df["accepted"].sum()))
        overall_rate = (df["accepted"].sum() / df["suggested"].sum() * 100) if df["suggested"].sum() else 0
        col6.metric("Overall Acceptance Rate (%)", f"{overall_rate:.2f}")
        
        # --- Charts ---
        st.subheader("User Activity Over Time")
        df_time = df.groupby("date")[["active", "engaged", "inactive"]].sum().reset_index()
        chart1 = alt.Chart(df_time).transform_fold(
            ['active', 'engaged', 'inactive'],
            as_=['Metric', 'Count']
        ).mark_line(point=True).encode(
            x='date:T',
            y='Count:Q',
            color='Metric:N',
            tooltip=['date:T', 'Metric:N', 'Count:Q']
        ).properties(width=700, height=400)
        st.altair_chart(chart1, use_container_width=True)
        
        st.subheader("Code Completions Over Time")
        df_code = df.groupby("date")[["suggested", "accepted"]].sum().reset_index()
        chart2 = alt.Chart(df_code).transform_fold(
            ['suggested', 'accepted'],
            as_=['Type', 'Lines']
        ).mark_bar().encode(
            x='date:T',
            y='Lines:Q',
            color='Type:N',
            tooltip=['date:T', 'Type:N', 'Lines:Q']
        ).properties(width=700, height=400)
        st.altair_chart(chart2, use_container_width=True)
        
        st.subheader("Acceptance Rate Over Time")
        
        # Calculate overall acceptance rate by date
        df_rate_overall = df.groupby("date").agg({
            "accepted": "sum",
            "suggested": "sum"
        }).reset_index()
        df_rate_overall["acceptance_rate"] = (df_rate_overall["accepted"] / df_rate_overall["suggested"] * 100)
        df_rate_overall["org"] = "Overall"
        
        # Calculate per-org acceptance rate by date
        df_rate_org = df.groupby(["date", "org"]).agg({
            "accepted": "sum",
            "suggested": "sum"
        }).reset_index()
        df_rate_org["acceptance_rate"] = (df_rate_org["accepted"] / df_rate_org["suggested"] * 100)
        
        # Combine overall and per-org rates
        df_rate_combined = pd.concat([df_rate_overall[["date", "org", "acceptance_rate"]], 
                                    df_rate_org[["date", "org", "acceptance_rate"]]])
        
        # Create the combined chart
        chart3 = alt.Chart(df_rate_combined).mark_line(point=True).encode(
            x='date:T',
            y=alt.Y('acceptance_rate:Q', title='Acceptance Rate (%)'),
            color=alt.Color('org:N', title='Organization'),
            tooltip=['date:T', 'org:N', alt.Tooltip('acceptance_rate:Q', format='.1f')]
        ).properties(
            width=700,
            height=400
        )
        
        st.altair_chart(chart3, use_container_width=True)
        
        # --- Code Metrics ---
        st.subheader("Code Metrics")
        lang_df = helpers.load_code_metrics(records, sel_editors, sel_models, sel_languages)
        if lang_df.empty:
            st.info("No code metrics available for selected filters.")
        else:
            # Show top 10 languages by volume
            top_df = lang_df.head(5)

            # Create chart
            chart = alt.Chart(top_df).mark_bar().encode(
                x=alt.X('Language:N', sort='-y'),
                y=alt.Y('Acceptance Rate:Q', title='Acceptance Rate (%)'),
                color=alt.Color('Language:N', legend=None),
                tooltip=[
                    alt.Tooltip('Language:N'),
                    alt.Tooltip('Acceptance Rate:Q', format='.1f'),
                    alt.Tooltip('Suggested Lines:Q', format=','),
                    alt.Tooltip('Accepted Lines:Q', format=',')
                ]
            ).properties(
                title='Acceptance Rate by Language (Top 10 by Volume)',
                width=700,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)

            # Show detailed stats table
            st.subheader("Detailed Statistics")
            st.dataframe(
                top_df.style.format({
                    'Acceptance Rate': '{:.1f}%',
                    'Suggested Lines': '{:,.0f}',
                    'Accepted Lines': '{:,.0f}'
                })
            )

if __name__ == "__main__":
    page1()