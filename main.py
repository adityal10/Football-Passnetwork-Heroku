from passnetwork import transform_data, plot_passes
from matchdata import get_data, get_match_names, extract_data, read_data, get_team_names, team_statistics
from heatmap import plot_heatmap

import pandas as pd
from statsbombpy import sb
from pathlib import Path
import requests

import streamlit as st


def main():
    # OPTIONS TO SELECT PARTICULAR SEASON BY THE USER

    competition_id, seasons = get_data(competition_name=competition)
    season = st.selectbox("Please select a season", seasons.keys(), index=None, placeholder="Select season")
    if season == '2022':
        season_id = seasons[season]
        st.caption(f'Season ID: {season_id}, Competition ID: {competition_id}')

        # SELECT BOX FOR MATCH IDS
        matches = get_match_names(competition_id=competition_id, season_id=season_id)
        match = st.selectbox("Please select a match", matches.keys(), index=None, placeholder="Select match")
        if match:
            match_id = matches[match]
            st.caption(f'Match: {match}, Match ID: {match_id}')

            # EXTRACTING DATA FROM GITHUB USING REQUESTS
            json_data = extract_data(match_id=match_id)

            # LOADING DATA FROM FOLDER
            df = read_data(match_id=match_id, json_data=json_data)
            # st.write(df)
                
            # PUTTING ANOTHER OPTION OF SELECTING WHICH TEAM TO SHOW THEIR PASSES
            teams = get_team_names(df)
            # team_name = st.selectbox("Please select a team", teams, index=None, placeholder="Select match")

            # FINALLY PLOTTING PASSES
            st.title("Plot passes")
            st.caption("This section plots the average passes done by the teams within their first substitution.")

            team_stat_dict = {}

            for i in range(len(teams)):
                team_name = teams[i]
                st.subheader(team_name)
                
                # GETTING STATS DATA 
                stat_dict = team_statistics(df=df, team_name=team_name)
                team_stat_dict[f'{team_name}'] = stat_dict
                st.caption(f"Pass network of {team_name}")

                # PLOTTING PASS NETWORK
                average_locations, pass_between, player_dict = transform_data(df=df, team_name=team_name)
                fig = plot_passes(average_locations, pass_between, player_dict)
                st.pyplot(fig)

            st.title("Summary Statistics")
            st.caption("This section deals with the normal statistics for the full game.")
            st.dataframe(team_stat_dict, use_container_width=True)

            st.title("Heatmaps")
            st.caption("You can see the heat maps of passes during that game")
            plot_heatmap(df, teams)
            
    else:
        st.warning("Select 2022 season")

if __name__ == '__main__':
    st.title("Football Pass Network")
    st.caption("This application works only for the season 2022 of FIFA world cup. Please select 2022 only. The other \
        the other seasons will be updated very soon!!")

    competition = st.selectbox("Please select a competition",['FIFA World Cup'],index=None,placeholder="Select competition")
    st.caption(f"You selected: {competition}")

    if competition:
        main()
