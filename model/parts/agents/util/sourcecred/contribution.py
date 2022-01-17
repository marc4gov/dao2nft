from enum import Enum

class Contribution(float,Enum):
  MILESTONE = 1
  PROPOSAL = 1/2
  ROI = 1
  TWITTER = 1/16
  DISCORD = 1/8
  GITHUB = 1/4
  PORT = 1/2
  VOTE = 1/2
  STAKE = 1
  LIQUIDITY_PROVISION = 1

class DiscordNodeWeight(Enum):
  TOPIC = 0
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