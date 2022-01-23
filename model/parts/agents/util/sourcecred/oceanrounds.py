round11_stats = {
  'projects': 22,
  'granted': 18,
  'new': 5,
  'max_votes': 652_000,
  'total_votes': 5_600_000,
  'total_stakeholders': 106
}

round12_stats = {
  'projects': 29,
  'granted': 28,
  'new': 12,
  'max_votes': 826_000,
  'total_votes': 3_970_000,
  'total_stakeholders': 71
}

round13_stats = {
  'projects': 33,
  'granted': 18,
  'new': 19,
  'max_votes': 941_000,
  'total_votes': 4_012_000,
  'total_stakeholders': 126
}

import scipy.stats
import numpy as np
import matplotlib.pyplot as plt

def probabilities(entities, mean, sigma, size):
  np.random.seed(1234)
  samples = np.random.lognormal(mean = mean,sigma = sigma, size = size)
  shape,loc,scale = scipy.stats.lognorm.fit(samples,floc=0)
  num_bins = entities
  counts,edges,patches = plt.hist(samples,bins=num_bins)
  cdf = scipy.stats.lognorm.cdf(edges,shape,loc=loc,scale=scale)
  prob = np.diff(cdf)
  return prob
