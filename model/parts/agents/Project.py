from .util.nft import Weight, NFT
from .util.wallet import Wallet
from .util.sourcecred.contribution import TaskType
from typing import List
from enum import Enum
import functools
import operator
import random

class TeamMemberType(Enum):
    PROJECT_LEAD = 1
    ENGINEER = 2
    LEAD_ENGINEER = 3
    COMMUNITY_LEAD = 4
    DESIGNER = 5

class TeamMember():
    def __init__(self, name: str, team_member_type:TeamMemberType, weight: float, timestep: int):
        self.weights = [Weight(weight, timestep)]
        self.nfts:List[NFT] = []
        self.current_weight = 0
        self.name = name
        self.type = team_member_type

    def reduceWeights(self, current_timestep):
        decayed_weigths = []
        for i in range(len(self.weights)):
            self.weights[i].decay(current_timestep)
            new_weight = self.weights[i].weight
            decayed_weigths.append(new_weight)
        self.current_weight = functools.reduce(operator.add, decayed_weigths)

    def __str__(self) -> str:
        s = []
        s += ["\nTeamMember={\n"]
        s += ['name=%s' % self.name]
        s += ['; type=%s' % self.type]
        s += ['; current_weight=%s' % self.current_weight]
        s += ['; weights=%s' % ",".join(map(str, self.weights))]
        s += [" \n/TeamMember}"]
        return "".join(s)

class Task(Weight):
    def __init__(self, taskType: TaskType, weight: float, timestep: int, workers:List[TeamMemberType]):
        super().__init__(weight, timestep)
        self.taskType = taskType
        self.delivered = False
        self.planned = timestep
        self.actual = 0
        self.workers: List[TeamMemberType] = workers

    def __str__(self) -> str:
        s = []
        s += ["\nTask={\n"]
        s += ['name=%s' % self.taskType]
        s += ['; weight=%s' % self.weight]
        s += ['; workers=%s' % ",".join(map(str, self.workers))]
        s += ['; planned=%s' % self.planned]
        s += ['; actual=%s' % self.actual]
        s += ['; delivered?=%s' % self.delivered]
        s += [" \n/Task}"]
        return "".join(s)

class Milestone:
    def __init__(self, nr: int, timestep: int):
        self.number = nr
        self.delivered = False
        self.planned = timestep
        self.actual = 0
        self.tasks:List[Task] = []

    def generateTasks(self, nr, current_timestep):
        if nr == 1:
            self.tasks.append(Task(TaskType.PLAN, 0.05, current_timestep + random.choice([5,7,9]), [TeamMemberType.PROJECT_LEAD]))
            self.tasks.append(Task(TaskType.DESIGN, 0.05, current_timestep + random.choice([8,9,10]), [TeamMemberType.DESIGNER]))
            return
        if nr == 2:
            self.tasks.append(Task(TaskType.RESEARCH, 0.05, current_timestep + random.choice([11,12,13]), [TeamMemberType.LEAD_ENGINEER]))
            self.tasks.append(Task(TaskType.CODE, 0.05, current_timestep + random.choice([14,16,18]), [TeamMemberType.ENGINEER]))
            return
        if nr == 3:
            self.tasks.append(Task(TaskType.MARKET, 0.05, current_timestep + random.choice([20,23,25]), [TeamMemberType.COMMUNITY_LEAD]))
            self.tasks.append(Task(TaskType.CODE, 0.05, current_timestep + random.choice([20,23,25]), [TeamMemberType.ENGINEER]))
            return
        
        self.tasks.append(Task(TaskType.MARKET, 0.05, current_timestep + random.choice([25,26,27]), [TeamMemberType.COMMUNITY_LEAD]))
        self.tasks.append(Task(TaskType.CODE, 0.05, current_timestep + random.choice([23,24,25]), [TeamMemberType.ENGINEER]))


    def __str__(self) -> str:
        s = []
        s += ["\nMilestone={\n"]
        s += ['nr=%s' % self.number]
        s += ['; tasks=%s' % ",".join(map(str, self.tasks))]
        s += ['; planned=%s' % self.planned]
        s += ['; actual=%s' % self.actual]
        s += ['; delivered?=%s' % self.delivered]
        s += [" \n/Milestone}"]
        return "".join(s)

class Project():
    def __init__(self, name: str, weight: float, timestep: int, wallet: Wallet):
        self.weights = [Weight(weight, timestep)]
        self.current_weight = 0
        self.name = name
        self.wallet = wallet
        self.finished = False
        self.team_members:List[TeamMember] = []
        self.nfts:List[NFT] = []
        self.voters = []
        self.rounds = []
        self.milestones:List[Milestone] = []

    def reduceWeights(self, current_timestep):
        decayed_weigths = []
        for i in range(len(self.weights)):
            self.weights[i].decay(current_timestep)
            new_weight = self.weights[i].weight
            decayed_weigths.append(new_weight)
        self.current_weight = functools.reduce(operator.add, decayed_weigths)

    def addMember(self, team_member):
        self.team_members.append(team_member)

    def addNFT(self, nft):
        self.nfts.append(nft)

    def addVoter(self, voterID):
        self.voters.append(voterID)

    def addRound(self, roundID):
        self.rounds.append(roundID)

    def addMilestone(self, milestone):
        self.milestones.append(milestone)

    def reset(self):
        self.milestones = []

    def generateMilestones(self, timestep):
        team_size = len(self.team_members)
        for i in range(team_size-1):
            milestone = Milestone(i+1, timestep)
            milestone.generateTasks(i+1, timestep)
            self.addMilestone(milestone)

    def __str__(self) -> str:
        s = []
        s += ["\nProject={\n"]
        s += ['name=%s' % self.name]
        s += ['; weight=%s' % self.current_weight]
        s += ['; wallet=%s' % self.wallet]
        s += [';\n milestones=%s' % ",".join(map(str, self.milestones))]
        s += [';\n team=%s' % ",".join(map(str, self.team_members))]
        s += [';\n grant rounds=%s' % ",".join(map(str, self.rounds))]
        s += [" \n/Project\n}"]
        return "".join(s)