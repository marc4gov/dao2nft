import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import numpy as np

def reverse_sigmoid(x):
    z = np.exp(x)
    sig = 2 / (1 + z)
    return sig

def decay_plot():
  x = np.arange(0,60)
  y = reverse_sigmoid(0.1 * x)
  plt.figure(figsize=(10,6))
  plt.xlabel('Days')
  plt.ylabel('Weight')
  plt.plot(x,y,label="Decay")
  plt.legend()
  plt.title('Partial Sigmoid function for decay in weights')



def monte_carlo_plot(dfs, column):
  fig, ax = plt.subplots()
  x = pd.Series(dfs[0]["timestep"]).values
  for df in dfs:
    ax.plot(x, pd.Series(df[column]).values, label='Run '+ str(df['run'][0])) 
  plt.xlabel('Timestep')
  plt.ylabel(column)
  ax.legend()
  plt.title(' ' + column)
  plt.show()


def agent_plot(experiment):
    """
For any agent 
    """
    df = experiment
    projects_df = df.projects
    ldf = pd.concat([projects_df,df.timestep], axis=1)
    pdf = ldf.projects.apply(pd.Series)

    for column in pdf:
        df2 = pd.DataFrame([vars(f) for f in pdf[agent]])
        df3 = pd.DataFrame([vars(f) for f in df2._wallet])
    edf = pd.concat([df3._USD, df3._ETH, df.timestep], axis=1, keys = ['USD', 'ETH', 'Timestep'])
        

    plt.figure(figsize=(20,6))
    plt.subplot(141)
    plt.plot(edf["Timestep"],edf["USD"],label=agent)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset USD')

    plt.subplot(142)
    plt.plot(edf["Timestep"],edf["ETH"],label=agent)
    plt.xlabel('Timestep')
    plt.ylabel('Reserves')
    plt.legend()
    plt.title('Asset ETH')
       
    plt.show()


def monte_carlo_plot(dfs, pool=True, pool_agent='White Pool', agent='Trader', asset="USD"):
  fig, ax = plt.subplots()
  edfs = []
  for df in dfs:
    edf = make_df(df, pool=pool, pool_agent=pool_agent, agent=agent)
    edfs.append(edf)
  x = pd.Series(edf["Timestep"]).values
  for ed in edfs:
    ax.plot(x, pd.Series(ed[asset]).values) 
  plt.xlabel('Timestep')
  plt.ylabel(asset)
  if pool:
    plt.title('Reserve ' + asset + ' for ' + pool_agent)
  else:
    plt.title('Volume ' + asset + ' for ' + agent)
  plt.show()