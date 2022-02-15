import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def monte_carlo_plot(dfs, column, column2):
  fig, ax = plt.subplots()
  x = pd.Series(dfs[0]["timestep"]).values
  for df in dfs:
    ax.plot(x, pd.Series(df[column]).values, label='Run '+ str(df['run'][0])) 
    ax.plot(x, pd.Series(df[column2]).values, label='Performer '+ str(df['substep'][0])) 
  plt.xlabel('Timestep')
  plt.ylabel(column)
  ax.legend()
  plt.title(' ' + column)
  plt.show()