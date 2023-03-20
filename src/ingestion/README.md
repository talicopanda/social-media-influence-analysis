# Ingestion

This directory holds the logic for

1. reading in twitter data in the format of SNACES. This format includes 3 relevant files: UserTweets, User
2. transforming the data in the following ways:

   - For each tweet, calcuate all content embedding strategies and write it to file
   - For each user, calculate their supply and demand

3. Writing the data from step 2 to MongoDB
