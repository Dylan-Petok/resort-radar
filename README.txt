Resort Radar!

Purpose: Tracking general sentiment for the most popular snowboarding resorts in the United States FOR THE PAST YEAR.
This is not all time reddit posts for resorts, just for the past year. Using posts from "TOP" and "THIS YEAR" filter.


General Flow :

Extract Data using PRAW Reddit API
Clean Data using Pandas
Store cleaned data as structured data in Snowflake
Load cleaned data back in here, and then use a Hugging Face model to analyze sentiment for cleaned data
Store data back in snowflake


Potential Issues/ Things need to do:
Make sure content being analyzed is accurate:
    -Mutliple Resorts in a post
    -Unrelated topics in post skewing sentiment for Resort mentioned in post -> might want to analyze which parts of a post refer to the resort or which parts are irrelveant in the post

Make website to put tableau worksheets in 

Make CI/CD workflow

Make docker container
