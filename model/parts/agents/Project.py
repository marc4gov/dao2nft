from .util.nft import Weight, NFT
from .util.wallet import Wallet
from .util.sourcecred.contribution import TaskType
from typing import List
from enum import Enum

class TeamMemberType(Enum):
    PROJECT_LEAD = 1
    ENGINEER = 2
    LEAD_ENGINEER = 3
    COMMUNITY_LEAD = 4
    DESIGNER = 5

class TeamMember(Weight):
    def __init__(self, name: str, team_member_type:TeamMemberType, weight: float, timestep: int):
        super().__init__(weight, timestep)
        self.name = name
        self.type = team_member_type

    def __str__(self) -> str:
        s = []
        s += ["\nTeamMember={\n"]
        s += ['name=%s' % self.name]
        s += ['; type=%s' % self.type]
        s += ['; weight=%s' % self.weight]
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
            self.tasks.append(Task(TaskType.PLAN, 0.01, current_timestep + 5, [TeamMemberType.PROJECT_LEAD]))
            self.tasks.append(Task(TaskType.DESIGN, 0.01, current_timestep + 10, [TeamMemberType.DESIGNER]))
            return
        if nr == 2:
            self.tasks.append(Task(TaskType.RESEARCH, 0.01, current_timestep + 15, [TeamMemberType.LEAD_ENGINEER]))
            self.tasks.append(Task(TaskType.CODE, 0.01, current_timestep + 25, [TeamMemberType.ENGINEER]))
            return
        if nr == 3:
            self.tasks.append(Task(TaskType.MARKET, 0.01, current_timestep + 25, [TeamMemberType.COMMUNITY_LEAD]))
            self.tasks.append(Task(TaskType.CODE, 0.01, current_timestep + 25, [TeamMemberType.ENGINEER]))
            return
        
        self.tasks.append(Task(TaskType.MARKET, 0.01, current_timestep + 30, [TeamMemberType.COMMUNITY_LEAD]))
        self.tasks.append(Task(TaskType.CODE, 0.01, current_timestep + 30, [TeamMemberType.ENGINEER]))


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

class Project(Weight):
    def __init__(self, name: str, weight: float, timestep: int, wallet: Wallet):
        super().__init__(weight, timestep)
        self.name = name
        self.wallet = wallet
        self.team_members:List[TeamMember] = []
        self.nfts:List[NFT] = []
        self.voters = []
        self.rounds = []
        self.milestones:List[Milestone] = []

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

    def generateMilestones(self, timestep):
        team_size = len(self.team_members)
        print(team_size)
        for i in range(team_size-1):
            milestone = Milestone(i+1, timestep)
            milestone.generateTasks(i+1, timestep)
            self.addMilestone(milestone)

    def __str__(self) -> str:
        s = []
        s += ["\nProject={\n"]
        s += ['name=%s' % self.name]
        s += ['; weight=%s' % self.weight]
        s += ['; wallet=%s' % self.wallet]
        s += [';\n milestones=%s' % ",".join(map(str, self.milestones))]
        s += [';\n team=%s' % ",".join(map(str, self.team_members))]
        s += [';\n grant rounds=%s' % ",".join(map(str, self.rounds))]
        s += [" \n/Project\n}"]
        return "".join(s)