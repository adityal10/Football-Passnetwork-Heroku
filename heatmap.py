from statsbombpy import sb
from pathlib import Path
import requests

import streamlit as st
import mplsoccer
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors


def plot_heatmap(df, teams):
    pitch = mplsoccer.VerticalPitch(pitch_type='opta', pitch_color='#22312b', line_color='#c7d5cc', line_zorder=2)
    
    # fig, axs = pitch.draw(ncols=2, figsize=(10, 7), constrained_layout=False, tight_layout=True)
    fig, axs = pitch.grid(ncols=2, axis=False)
    fig.set_facecolor('#22312b')

    for i, team in enumerate(teams):
        # df = df.copy()
        team_df = df[(df['team']==team) & (df['type']=='Pass')] # & (df['pass_outcome']=='Successfull')

        team_df['pass_outcome'] = team_df['pass_outcome'].fillna("Successfull")

        # CREATED 4 NEW COLUMNS OF THE PASSES LOCATION DONE BY TEAM
        team_df[['x_start', 'y_start']] = pd.DataFrame(team_df.location.tolist(), index=team_df.index)
        team_df[['x_end', 'y_end']] = pd.DataFrame(team_df.pass_end_location.tolist(), index=team_df.index)

        customcmap = matplotlib.colors.LinearSegmentedColormap.from_list('custom cmap',['black', 'red'])

        pitch.kdeplot(x=team_df['x_start'], y=team_df['y_start'], ax=axs['pitch'][i],fill=True, levels=100,
                        zorder=1,cmap='Reds', thresh=0.15)
        # Add title for each subplot
        axs['pitch'][i].set_title(f"{team} Passes Heatmap", color='white')
        axs['title'].text(0.5, 0.7, f"Pass Heatmap of {teams[0]} & {teams[1]}", color='white',
                  va='center', ha='center', fontsize=20)
        
    st.pyplot(fig)