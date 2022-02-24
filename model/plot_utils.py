import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import copy
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

def arrange_projects(p1: pd.DataFrame, p2: pd.DataFrame):
  for p in list(p2.columns):
    if p in list(p1.columns):
      index = list(p1.columns).index(p)
      prev_index = list(p2.columns).index(p)
      col = p2.pop(p)
      if index < len(list(p2.columns)):
        prev = list(p2.columns)[index]
        p2.insert(index, col.name, col)
        col2 = p2.pop(prev)
        p2.insert(prev_index, col2.name, col2 )
      else:
        p2.insert(len(list(p2.columns)), col.name, col)
  return(p2)

def project_dfs(df, rounds, subsets=1):
  dfps = [[copy.deepcopy(pd.DataFrame) for x in range(subsets)] for y in range(rounds)]
  for i in range(rounds):
    for j in range(subsets):
      dx = df[(df["round"] == i+1) & (df["subset"] == j)]
      dfps[i][j] = dx['projects'].apply(pd.Series)
      dfps[i][j].rename(columns=lambda x: x.split(" ")[1], inplace=True)
      if i > 0:
        dfps[i][j] = arrange_projects(dfps[i-1][j], dfps[i][j])
      dfps[i][j].reset_index(drop=True, inplace=True)
      s = dfps[i][j].shape
      for k in range(s[0]):
        for m in range(s[1]):
          dfps[i][j].loc[k][m] = dfps[i][j].loc[k][m].current_weight
  return dfps

def project_plot(df, rounds, subsets=1):
  dfps = project_dfs(df, rounds, subsets)
  x = [ dfps[i][j].shape for i in range(rounds) for j in range(subsets)]
  max(x)[1]
  for i in range(rounds):
      for j in range(subsets):
        diff = max(x)[1] - dfps[i][j].shape[1]
        for k in range(diff):
          dfps[i][j].insert(len(dfps[i][j].columns),'zeros ' + str(k+1), [0.0 for m in range(30)])
  fig, axes = plt.subplots(nrows=max(x)[1],ncols=rounds,figsize=(20,60))
  for i in range(rounds):
      flag = True
      for j in range(subsets):
        dfps[i][j].plot.line(ax = axes[:,i], subplots=True, legend=True)


def voter_dfs(df, rounds, subsets=1):
  dfps = [[copy.deepcopy(pd.DataFrame) for x in range(subsets)] for y in range(rounds)]
  for i in range(rounds):
    for j in range(subsets):
      dx = df[(df["round"] == i+1) & (df["subset"] == j)]
      dfps[i][j] = dx['projects'].apply(pd.Series)
      dfps[i][j].rename(columns=lambda x: x.split(" ")[1], inplace=True)
      if i > 0:
        dfps[i][j] = arrange_projects(dfps[i-1][j], dfps[i][j])
      dfps[i][j].reset_index(drop=True, inplace=True)
      s = dfps[i][j].shape
      for k in range(s[0]):
        for m in range(s[1]):
          dfps[i][j].loc[k][m] = dfps[i][j].loc[k][m].current_weight
  return dfps