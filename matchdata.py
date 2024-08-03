from statsbombpy import sb
import requests
from pathlib import Path
import pandas as pd
import streamlit as st


def get_data(competition_name):
    # GETTING ALL THE COMPETITIONS DATASET FROM STATSBOMB
    comp = sb.competitions()

    # TAKING LA LIGA AND CHAMPIONS LEAGUE INTO CONSIDERATION
    df = comp[(comp['competition_name']==competition_name)]

    # MAKING DICTIONARY OF COMPETITIONS AND SEASONS IDS
    competitions = df.drop_duplicates('competition_name').set_index('competition_name')['competition_id'].to_dict()
    competition_id = competitions[competition_name]

    seasons = df.drop_duplicates('season_name').set_index('season_name')['season_id'].to_dict()

    return competition_id, seasons

def get_match_names(competition_id, season_id):
    df = sb.matches(competition_id=competition_id, season_id=season_id)
    match_dict = {f"{row['home_team']} vs {row['away_team']}":row['match_id'] for _, row in df.iterrows()}

    return match_dict

def extract_data(match_id):
    try:
        url = f'https://raw.githubusercontent.com/statsbomb/open-data/master/data/three-sixty/{match_id}.json'
        directory = Path('./match_info')
        file_path = directory / f'{match_id}.json'
        
        # Create the directory if it doesn't exist
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        
        # Check if the file already exists
        if file_path.is_file():
            st.caption("File already exists")
        else:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
            
            # Write the content to a file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            st.caption(f'Saved data for match {match_id}')
    
    except requests.exceptions.RequestException as e:
        st.caption(f'Error Occurred during data extract: {e}')
        st.caption(f'Please select only the season 2022')
    
    return file_path

def read_data(match_id, file_path):
    match_360_df = pd.read_json(file_path)
    match_events_df = sb.events(match_id=match_id)

    df = pd.merge(left=match_events_df, right=match_360_df, left_on='id', right_on='event_uuid', how='left')

    return df

def get_team_names(df):
    return list(df.team.unique())

def team_statistics(df, team_name):
    
    stat_dict = {}

    team_df = df[df['team'] == team_name]

    # FILLING MISSING VALUES IN PASSOUTCOME AS SUCCESSFUL
    team_df['pass_outcome'] = team_df['pass_outcome'].fillna('Successful')

    # TOTAL PASSES
    team_pass = team_df[team_df['type']=="Pass"]
    # st.write(f"Total passes: {len(team_pass)}")
    stat_dict['Total Passes'] = len(team_pass)

    # TOTAL SUCCESSULL PASSES DONE
    team_pass_succ = team_pass[team_pass['pass_outcome']=='Successful']
    stat_dict['Total successful passes'] = len(team_pass_succ)

    # PASS PERCENTAGE
    stat_dict['Pass Successull %'] = float(round(stat_dict['Total successful passes'] / stat_dict['Total Passes'],2)*100)

    # PLAY PATTERN
    play_pattern = team_df.play_pattern.value_counts().to_dict()
    for key, value in play_pattern.items():
        stat_dict[key] = value

    # SHOT OUTCOMES
    shot_outcomes = team_df.shot_outcome.value_counts().to_dict()
    for key, value in shot_outcomes.items():
        stat_dict[key] = value
    
    return stat_dict 