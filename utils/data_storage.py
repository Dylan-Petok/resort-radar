import snowflake.connector
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import os

sf_user = user=os.getenv('SNOWFLAKE_USER')
sf_pass = password=os.getenv('SNOWFLAKE_PASS')
sf_acc = account=os.getenv('SNOWFLAKE_ACCOUNT')

#encoded password for url
sf_pass_e = urllib.parse.quote(os.getenv('SNOWFLAKE_PASS')) 


def store_data(cleaned_results):
    
    try:
        #connect to snowflake
        conn = snowflake.connector.connect(
            user=sf_user,
            password=sf_pass,
            account=sf_acc,
            warehouse='COMPUTE_WH',
            database='RESORTRADAR',
            schema='PUBLIC',
            role="ACCOUNTADMIN"
        )

        cursor = conn.cursor()

        # Iterate over cleaned data and insert into Snowflake
        for resort, posts in cleaned_results.items():
            for post in posts:
                insert_query = """
                    INSERT INTO cleaned_posts (RESORT, TITLE, P_TEXT, SCORE, CREATED)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    post["resort"],
                    post["title"],
                    post["text"],
                    post["score"],
                    post["created_utc"]
                ))

        conn.commit()
        cursor.close()
        conn.close()
        print("Cleaned data loaded into Snowflake successfully.")
        return True
    except Exception as e:
        print(e)
        return False

def load_cleaned_data():
    try:
        conn = snowflake.connector.connect(
            user='dpetok',
            password='Shotzie88@',
            account='szbdsib-nrb28809',
            warehouse='COMPUTE_WH',
            database='RESORTRADAR',
            schema='PUBLIC',
            role="ACCOUNTADMIN"
        )
        cursor = conn.cursor()

        query = "SELECT * from cleaned_posts"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = pd.DataFrame(cursor.fetchall(), columns=columns)

        conn.close()
        cursor.close
        print("Cleaned data loaded into Snowflake successfully.")
        return data

    except Exception as e:
        print(e)
        return False


def store_sentiment_data(dataframe):
    try:
        # Create a connection engine
        engine = create_engine(
            f'snowflake://{sf_user}:{sf_pass_e}@{sf_acc}/RESORTRADAR/PUBLIC'
        )
        print(engine)
        dataframe.to_sql(
            name='sentiment_data',  #snowflake table name
            con=engine,
            if_exists='replace',  # 'replace' to overwrite, 'append' to add rows
            index=False
        )
        print("Sentiment analysis data loaded into Snowflake successfully.")
        return True
    except Exception as e:
        print(e)
        return False