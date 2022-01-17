def make_contributor(name, contributions):
  contributor = {
    'name': name,
    'contributions': contributions
  }
  return contributor

def add_contribution(contributor, contribution):
  contributor.append(contribution)
  return contributor