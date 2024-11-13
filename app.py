import streamlit as st
import pandas as pd

# Function to load the Excel file
def load_data(file):
    df = pd.read_excel(file)
    return df

# Function to filter games by odds with ±0.15 tolerance for all 3 outcomes
def filter_matches_all(df, home_odds_input, draw_odds_input, away_odds_input, tolerance=0.15):
    df[1] = pd.to_numeric(df[1], errors='coerce')  # Home Odds (column 1)
    df['X'] = pd.to_numeric(df['X'], errors='coerce')  # Draw Odds (column 'X')
    df[2] = pd.to_numeric(df[2], errors='coerce')  # Away Odds (column 2)
    
    filtered_df = df[
        (df[1].between(home_odds_input - tolerance, home_odds_input + tolerance)) &
        (df['X'].between(draw_odds_input - tolerance, draw_odds_input + tolerance)) &
        (df[2].between(away_odds_input - tolerance, away_odds_input + tolerance))
    ]
    
    return filtered_df

# Function to filter games by odds with ±0.15 tolerance for at least 2 outcomes
def filter_matches_two_of_three(df, home_odds_input, draw_odds_input, away_odds_input, tolerance=0.15):
    df[1] = pd.to_numeric(df[1], errors='coerce')  # Home Odds (column 1)
    df['X'] = pd.to_numeric(df['X'], errors='coerce')  # Draw Odds (column 'X')
    df[2] = pd.to_numeric(df[2], errors='coerce')  # Away Odds (column 2)
    
    condition_home = df[1].between(home_odds_input - tolerance, home_odds_input + tolerance)
    condition_draw = df['X'].between(draw_odds_input - tolerance, draw_odds_input + tolerance)
    condition_away = df[2].between(away_odds_input - tolerance, away_odds_input + tolerance)
    
    filtered_df = df[(condition_home & condition_draw) | 
                     (condition_home & condition_away) | 
                     (condition_draw & condition_away)]
    
    return filtered_df

# Function to determine if both teams scored at least one goal (Qol/Qol)
def add_qol_column(df):
    def qol_check(score):
        try:
            home_goals, away_goals = map(int, str(score).split(':'))  # Split the score into home and away goals
            return 'Yes' if home_goals > 0 and away_goals > 0 else 'No'
        except ValueError:
            return 'No'  # In case the score is missing or not in the correct format

    df['Qol/Qol'] = df['Hesab'].apply(qol_check)
    return df

# Function to add "Ust" and "Alt" columns based on total goals
def add_ust_alt_columns(df):
    def ust_check(score):
        try:
            home_goals, away_goals = map(int, str(score).split(':'))
            return "Yes" if home_goals + away_goals > 2.5 else "No"
        except (ValueError, AttributeError):
            return "No"  # Default if the score format is invalid

    def alt_check(score):
        try:
            home_goals, away_goals = map(int, str(score).split(':'))
            return "No" if home_goals + away_goals > 2.5 else "Yes"
        except (ValueError, AttributeError):
            return "No"  # Default if the score format is invalid

    # Apply functions separately to generate "Ust" and "Alt" columns
    df['Ust'] = df['Hesab'].apply(ust_check)
    df['Alt'] = df['Hesab'].apply(alt_check)
    return df

# UI for the app
st.title("Match Odds Filter")

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")

if uploaded_file:
    df = load_data(uploaded_file)
    st.write("Data Loaded Successfully!")
    st.write(df.head())

    # User inputs
    home_odds = st.number_input("Enter the home team odds:")
    draw_odds = st.number_input("Enter the draw odds:")
    away_odds = st.number_input("Enter the away team odds:")
    tolerance = st.slider("Set tolerance:", 0.1, 0.5, 0.15)
    filter_mode = st.radio("Choose filtering mode", ['all', 'two'])

    # Run the filter when button is clicked
    if st.button("Filter Matches"):
        if filter_mode == 'all':
            result_df = filter_matches_all(df, home_odds, draw_odds, away_odds, tolerance)
        elif filter_mode == 'two':
            result_df = filter_matches_two_of_three(df, home_odds, draw_odds, away_odds, tolerance)
        
        # Add "Qol/Qol" column to the filtered data
        result_df = add_qol_column(result_df)
        
        # Add "Ust" and "Alt" columns to the filtered data
        result_df = add_ust_alt_columns(result_df)

        # Add a custom index column starting from 1
        result_df = result_df.reset_index(drop=True)
        result_df.index += 1
        result_df.index.name = "Index"

        # Reorder columns to display "Qol/Qol", "Ust", and "Alt" as needed
        result_df = result_df[['Oyunlar', 'Hesab', 1, 'X', 2, 'Qol/Qol', 'Ust', 'Alt', 'Tarix']]
        
        # Display results
        if result_df.empty:
            st.write("No matches found with the specified odds.")
        else:
            st.write("Filtered Results:")
            st.write(result_df)
