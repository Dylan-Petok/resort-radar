# resort dictionary with nicknames
top_ten = {
    "Breckenridge": ["Breck", "Breckenridge"],
    "Aspen Snowmass": ["Aspen", "Snowmass"],
    "Mammoth Mountain": ["Mammoth"],
    "Park City": ["Park City", "PCMR"],
    "Vail": ["Vail"],
    "Jackson Hole": ["Jackson", "Jackson Hole", "JHMR", "J Hole"],
    "Lake Tahoe Resorts": ["Lake Tahoe", "Tahoe"],
    "Big Sky": ["Big Sky"],
    "Killington": ["Killington", "Killy"],
    "Snowbird": ["Snowbird"],
}


def extract_data(reddit):
    # seeing if function works
    print("extract data function")

    # initialize results dictionary
    results = {}
    target_limit = 5
    fetch_limit_multiplier = 3
    fetch_limit = (
        target_limit * fetch_limit_multiplier
    )  # Calculate number of posts to fetch.. example: we want a limit of 5 posts but we fetch 15 to account for posts
    # that MAY be just image posts, as we want text based posts

    for resort, nicknames in top_ten.items():
        query = " OR ".join(nicknames)  # make query for search
        subreddit = reddit.subreddit("snowboarding")
        resort_posts = []  # init posts list

        try:
            # Fetch top posts for resort
            for post in subreddit.search(
                query=query, sort="top", time_filter="year", limit=fetch_limit
            ):

                if not post.selftext.strip():
                    continue

                # append post to list
                resort_posts.append(
                    {
                        "resort": resort,
                        "title": post.title,
                        "text": post.selftext,
                        "score": post.score,
                        "created_utc": post.created_utc,
                    }
                )

                # Stop once the target limit is reached
                if len(resort_posts) >= target_limit:
                    break
        except Exception as e:
            print(f"Error fetching data for {resort}: {e}")

        # store data in results
        results[resort] = resort_posts

    return results
