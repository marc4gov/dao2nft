from model.parts.agents.util.sourcecred.contributor import generate_project_weights, check_milestones, generate_project, change_graph, expand_graph, do_contribution_action, do_discord_action, do_github_action, get_team_weight
from model.parts.agents.Project import Project
from model.parts.agents.util.nft import Weight
from typing import List, Dict
import networkx as nx
import math
import random


def projects_policy(params, step, sH, s):
    """
    Update the projects state.
    """
    current_timestep = len(sH)
    timestep_per_day = 1
    timestep_per_week = 7
    timestep_per_month = 30

    dao_graph:nx.Graph = s['dao_graph']
    projects:Dict[str, Project] = s['projects']
    round = s['round']

    # new Grants round each month
    if (current_timestep % timestep_per_month) == 0:
      round += 1
      # generate new projects
      project_weights, total_stakeholders, total_votes = generate_project_weights(round)
      
      # recurring means how many projects will continue for the next round
      # recurring = params['recurring_factor']
      recurring = 0.5
      # print("Recurring: ", recurring)
      recurring_factor = math.floor(recurring * len(projects))
      recurring_project_names = random.sample(list(projects), recurring_factor)
      recurring_projects_total_weight = 0
      recurring_projects = {}
      for name in recurring_project_names:
        recurring_projects[name] = projects[name]
        recurring_projects_total_weight += projects[name].weight
        # print(recurring_projects[name])

      # new entrant selection
      new_factor = math.floor((1-recurring) * len(project_weights))
      new_entrants_names = random.sample(list(project_weights), new_factor)
      new_entrants_total_weight = 0
      new_entrants = {}
      for name in new_entrants_names:
        new_entrants[name] = project_weights[name]
        new_entrants_total_weight += project_weights[name]
      # weights are offset because of random selections
      missing_weight = 1 - (recurring_projects_total_weight + new_entrants_total_weight)
      total_new_entrants = len(new_entrants) if len(new_entrants) > 0 else 1
      total_recurring_projects = len(recurring_projects) if len(recurring_projects) > 0 else 1
      missing_weight_per_project = missing_weight/(total_new_entrants + total_recurring_projects)
      # init the new entrants
      for name, weight in new_entrants.items():
        new_weight = weight + missing_weight_per_project
        team = generate_project(name, new_weight, current_timestep, math.floor(total_votes * weight))
        new_entrants[name] = team
        dao_graph.add_node(name)
        dao_graph.add_edge('Round ' + str(round), name)
      # adjust weights and milestones per project in recurring projects
      for name, project in recurring_projects.items():
        project.weight += missing_weight_per_project
        project.reset()
        project.generateMilestones(current_timestep)
        recurring_projects[name] = project
        
      # merge the new entrants and the recurring projects
      projects = {**recurring_projects, **new_entrants}
      dao_graph = expand_graph(dao_graph, projects)
      return ({
          'projects': projects,
          'dao_graph': dao_graph,
          'round': round
      })

    # actions in projects by week
    if (current_timestep % timestep_per_week) == 0:
      for project in projects.values():
        # check milestones progress
        pass

    # actions in projects by day
    for project_name, project in projects.items():
      milestones = []
      # check milestones & tasks in progress
      projects[project_name].milestones = check_milestones(projects[project_name].milestones, current_timestep)
      members = []
      for member in project.team_members:
        # do an action per team member (in 50% of the time) or nothing (in 50% of the time)
        new_weight = random.choice([do_discord_action(), do_github_action(), do_contribution_action(), 0, 0, 0])
        if new_weight > 0:
          member.weights.append(Weight(new_weight, current_timestep))
          member.reduceWeights(current_timestep)
        members.append(member)
      new_project_weight = get_team_weight(members, current_timestep)
      project.team_members = members
      project.weight = new_project_weight
      projects[project_name] = project
      dao_graph = change_graph(dao_graph, project)
      dao_graph.nodes[project_name]['weight'] = project.weight

    return ({
      'projects': projects,
      'dao_graph': dao_graph,
      'round': round
    })
