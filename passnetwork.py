import pandas as pd
from mplsoccer import Pitch
import streamlit as st

def transform_data(df, team_name, pass_type='Pass'):
  """
  This function transforms data into different seperate dataframes for successfull
  outcome passes and average location of the players within the first subsition
  taken place.
  """
  team = df[(df['team']==team_name) & (df['type']==pass_type)].reset_index(drop=True)

  # CREATED 4 NEW COLUMNS OF THE PASSES LOCATION DONE BY ARGENTINA
  team[['x_start', 'y_start']] = pd.DataFrame(team.location.tolist(), index=team.index)
  team[['x_end', 'y_end']] = pd.DataFrame(team.pass_end_location.tolist(), index=team.index)

  # WE FILL THE MISSING VALUES IN PASS_OUTCOME COLUMN BY SUCCESSFULL FOR EVERY SUCCESSFULL PASS
  team['pass_outcome'] = team['pass_outcome'].fillna('Successful')

  # CREATING A NEW COLUMN OF THE PLAYER TO PASSED THE BALL
  team['passer'] = team['player_id']

  # CREATING A NEW COLUMNS OF THE PLAYER WHO RECIEVED THE BALL
  team['recipient'] = team['player_id'].shift(-1)

  # CREATING SEPERATE DATAFRAMES FOR SUCCESFULL PASSES
  passes = team[team['type']=='Pass']
  successfull = passes[passes['pass_outcome']=='Successful']

  # GETTING THE TIME OF THE FIRST SUBSTITUTION MADE IN THE GAME
  subs = df[(df['team']==team_name) & (df['type']=='Substitution')].reset_index(drop=True)
  subs = subs['minute']
  firstSub = subs.min()

  # st.write(f"{team_name} made their 1st substitution within {firstSub} mins.")

  # TAKING ONLY ALL PASSES BEFORE THE FIRST SUBSTITUTION MADE IN THE GAME
  # successfull = successfull[successfull['minute'] < firstSub]
  # st.write(f"Total number of successfull passes done by the team: {len(successfull)}.")


  # CONVERTING THE PASSER AND RECIPIENT DATATYPE FROM FLOAT -> INTEGER

  pas = pd.to_numeric(successfull['passer'], downcast='integer')
  rec = pd.to_numeric(successfull['recipient'], downcast='integer')

  successfull['passer'] = pas
  successfull['recipient'] = rec

  # THIS DATAFRAME GIVES US THE AVERAGE LOCATIONS OF THE PLAYER AND NUMBER OF PASSES DONE BY EACH PLAYER
  average_locations = successfull.groupby('passer').agg({ 'x_start':['mean'], 'y_start':['mean', 'count']})
  average_locations.columns = ['start_x', 'start_y', 'count']

  # THIS DATAFRAME GIVES US THE NUMBER OF SUCCESSFULL PASSES BETWEEN 2 PLAYERS
  pass_between = successfull.groupby(['passer', 'recipient']).id.count().reset_index()
  pass_between.rename(columns={'id':'pass_count'}, inplace=True)

  # WE THEN MERGE THE AVERAGE LOCATIONS DF WITH PASSES BETWEEN PLAYERS TO GET THE LOCATION
  pass_between = pass_between.merge(average_locations, left_on='passer', right_index=True)
  pass_between = pass_between.merge(average_locations, left_on='recipient', right_index=True, suffixes=['','_end'])

  # WE FILTER OUT PASSES BETWEEN PLAYER BY MORE THAN 3 PASSES
  pass_between = pass_between[pass_between['pass_count']>3]

  # TAKING PLAYER NAMES
  player_dict = passes.drop_duplicates('player_id').set_index('player_id')['player'].to_dict()

  return average_locations, pass_between, player_dict

def plot_passes(average_locations, pass_between, player_dict):
    # Setup the pitch
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
    fig, ax = pitch.draw(figsize=(10, 7), constrained_layout=False, tight_layout=True)
    fig.set_facecolor('#22312b')

    arrows = pitch.arrows(1.2*pass_between.start_x, .8*pass_between.start_y,
                            1.2*pass_between.start_x_end, .8*pass_between.start_y_end, ax=ax)

    nodes = pitch.scatter(1.2*average_locations.start_x, .8*average_locations.start_y, s=100, color='white', edgecolors='black', linewidth=1.5, ax=ax)

    # ANNOTE PLAYER NAMES
    for i, row in pass_between.iterrows():
        id = float(row['passer'])
        player_name = player_dict[id]
        ax.annotate(player_name, (row['start_x'], row['start_y']-1.5), textcoords="offset points", color='white')

    return fig