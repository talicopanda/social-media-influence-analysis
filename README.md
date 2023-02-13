# social-media-influence-analysis

# Workflow

1. Download and setup SNACES/core according to its documentation
2. Run 'Process Tweets' with the -vectorize option enabled to add word embedding vectors to processed tweets
3. Run ./SNACES.py, select Influence, then choose which functionality and give input as prompted.

There will be 3 main categories of functionality:

1. Graphing

- Graph a given user's demand curve
- Graph a given user's supply curve
- Graph a given communities's supply curve
- Graph a given communities's supply curve

2. Correlation

- Graph a two user's, one user and one community, or two communities', calculate correlation between either demand or supply curves

3. Causation

- Graph a two user's, one user and one community, or two communities', calculate causation between either demand or supply curves

Note that for passing in communities or influencer's, the user can input only the required information to find a community / influencer, and they will be found programatically by leveraging SNACES functionality.

# Plan:

Fork SNACES repo

- Change certain definitions, i.e processed tweet, to add processing on ingestion that matches our use cases as we want vectorized definitions on tweets
- Add functionality to SNACES.py that guides / gathers user input
- Call SNACES functionality (DetectCoreActivity, run_clustering) to compute required objects
- Run corresponding functionality defined in this repository with computed inputs
- Output to user or to database as directed by input

# Issues

Twitter API has readjusted pricing model -> new basic tier will cost $100/month
