import os
import urllib.parse

import pandas as pd
import snowflake.connector
from sqlalchemy import create_engine

sf_user = user = os.getenv("SNOWFLAKE_USER")
sf_pass = password = os.getenv("SNOWFLAKE_PASS", "")
sf_acc = account = os.getenv("SNOWFLAKE_ACCOUNT")

# encoded password for url
sf_pass_e = urllib.parse.quote(sf_pass)


def connect_snowflake():
    try:
        # connect to snowflake
        conn = snowflake.connector.connect(
            user=sf_user,
            password=sf_pass,
            account=sf_acc,
            warehouse="COMPUTE_WH",
            database="RESORTRADAR",
            schema="PUBLIC",
            role="ACCOUNTADMIN",
        )
        return conn
    except Exception as e:
        print("Error connecting to Snowflake:", e)
        raise  # This will stop execution and give you a full traceback


def store_data(cleaned_results):
    conn = connect_snowflake()
    cursor = conn.cursor()
    try:
        # Clear out the table before inserting new data.
        # TRUNCATE TABLE is generally faster than DELETE * from cleaned_posts and resets the table.
        cursor.execute("TRUNCATE TABLE cleaned_posts")
        conn.commit()
        # Iterate over cleaned data and insert into Snowflake
        for resort, posts in cleaned_results.items():
            for post in posts:
                insert_query = """
                        INSERT INTO cleaned_posts (RESORT, TITLE, P_TEXT, SCORE, CREATED)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                cursor.execute(
                    insert_query,
                    (
                        post["resort"],
                        post["title"],
                        post["text"],
                        post["score"],
                        post["created_utc"],
                    ),
                )

        conn.commit()
        cursor.close()
        conn.close()
        print("Cleaned data loaded into Snowflake successfully.")
        return True
    except Exception as e:
        print(f"[ISSUE]: Data Storage Query! : {e}")
        return False


def load_cleaned_data():
    conn = connect_snowflake()
    cursor = conn.cursor()
    try:
        query = "SELECT * from cleaned_posts"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = pd.DataFrame(cursor.fetchall(), columns=columns)

        print("Cleaned data loaded into Snowflake successfully.")
        return data

    except Exception as e:
        print(f"[ISSUE]: Clean Data Load Query : {e}")
        return False

    finally:
        conn.close()
        cursor.close()


def store_sentiment_data(dataframe):
    try:
        # Create a connection engine
        engine = create_engine(
            f"snowflake://{sf_user}:{sf_pass_e}@{sf_acc}/RESORTRADAR/PUBLIC"
        )
        print(engine)
        dataframe.to_sql(
            name="sentiment_data",  # snowflake table name
            con=engine,
            if_exists="replace",  # 'replace' to overwrite, 'append' to add rows
            index=False,
        )
        print("Sentiment analysis data loaded into Snowflake successfully.")
        return True
    except Exception as e:
        print(e)
        return False
