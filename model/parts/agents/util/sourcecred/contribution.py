from enum import Enum

# +
# MOST IMPORTANT ELEMENT: should try not to mix outcomes/deliverables and activities/processes, 
# should probably be split so you do not get a lot of reward for a 1000 tweets. 
# Likely we want to map agents, activities, outcomes.
# HOMEWORK: Study Sourcred document from Marc in chat and consider dimensions the the below and their weights to reach
# consensus Monday.

class Contribution(float,Enum): 
  MILESTONE = 1 #reaching a milestone : 1 = maximum weight
  PROPOSAL = 1/2 # nice with proposals, but have not delivered, but takes time and can be valuable so 50 pct
  ROI = 1 # execution delivered the value you promised, very nice
  TWITTER = 1/16 # from sourcecred, likely a bit high... perhaps 1/32... Marc will share the sourcecred baseline approach
  DISCORD = 1/8 # likely too high as well
  GITHUB = 1/4 # see nodeweights on what value different github contributions give.
  PORT = 1/2 # if you deliver to an Ocean port/showroom - see Oceanport website, a window for marketing
  VOTE = 1/2 # you want an active community, maybe we should get some creds for voting I become more active 
    # and we want energy in the system
  STAKE = 1 # staking tokens means taking risk, you get punished if project fails, but you should maybe have 
    # reward for exposing your tokens at risk by staking on the proposal - NOT the dataset. Creates dynamics
  LIQUIDITY_PROVISION = 1 # Staking on datasets. If you buy a dataset you should probably also be rewarded

# Set maximum for each outcome/activity so you have diminishing returns - an Augmented Bonding Curve (ABC)

class ProofOf(float, Enum):
  WORK = 1
  DOMAIN_EXPERTISE = 2
  COMMITMENT = 3
  RECRUITMENT = 4
  DEFENDER = 5
  IDEATION = 6
  
class NFT(Enum):
  BRONZE = 1
  SILVER = 2
  GOLD = 3
  DIAMOND = 4
  PLATINUM = 5

class OceanNFT(Enum):
  SHRIMP = 1
  OYSTER = 2
  FISH = 3
  DOLPHIN = 4
  FISHERMAN = 5
  MANTA = 6
  OCEAN = 7
  ATLANTIS = 8

class DiscordNodeWeight(Enum):
  TOPIC = 0 # Sourcecred default suggests a post is not valuable but a reaction has value. See article.
  POST = 0
  LIKE = 16

class DiscordEdgeWeight(float, Enum):
  POST_REPLIED_TO_BY = 1.0
  POST_IS_REPLY_TO = 1/16
  TOPIC_IS_AUTORED_BY = 1/8
  AUTHORS_TOPIC = 1
  POST_IS_AUTHORED_BY = 1/8
  AUTHORS_POST = 1
  IS_CONTAINED_BY_TOPIC = 1/16
  CONTAINS_POST = 1/4
  IS_LIKED_BY = 2
  LIKES = 1/16
  LIKE_CREATED_BY = 1
  CREATES_LIKE = 1/16
  POST_IS_REFERENCED_BY = 1/2
  REFERENCES_POST = 1/16
  TOPIC_IS_REFERENCED_BY = 1/2
  REFERENCES_TOPIC = 1/16
  IS_MENTIONED_BY = 1/4
  MENTIONS = 1/16


class GithubNodeWeight(Enum):
  REPOSITORY = 0
  ISSUE = 4
  PULL_REQUEST = 16
  PULL_REQUEST_REVIEW = 8
  COMMENT = 1
  COMMIT = 0
  BOT = 0

class GithubEdgeWeight(float, Enum):
  AUTHORS = 1
  IS_AUTHORED_BY = 1/16
  HAS_CHILD = 1/16
  HAS_PARENT = 1/4
  CONTAINS_POST = 1/4
  IS_MERGED_BY = 2
  MERGES = 1/16
  IS_REFERENCED_BY = 1/2
  REFERENCES = 1/16

contribution = {
  'topic': None,
  'type': None
}

edge = {
  'from': None,
  'to': None,
  'weight_to': None,
  'weight_from': None,
  'timestamp': None 
}