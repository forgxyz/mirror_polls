import pandas as pd
import json
import tweepy
import schedule
import subprocess
import time

# test comment
# run on pi with nohup python3 -u mirror.py > output.log &


def main():
    # load twitter api info
    with open('credentials.json') as f:
        creds = json.load(f)
        consumer_key = creds['consumer_key']
        consumer_secret = creds['consumer_secret']
        access_token = creds['access_token']
        access_token_secret = creds['access_token_secret']

    # init tweepy instance
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    # run cli to get current polls data
    out = subprocess.run(['mirrorcli', 'query', 'gov', 'polls'], capture_output=True, text=True)

    # jsonify
    res = json.loads(out.stdout)

    # load into dataframe
    df = pd.DataFrame(res['polls'])
    df = df.set_index('id')

    # load previous polls data
    prior = pd.read_pickle('mirror_data.pkl')

    # check for any new information
    for id in df.index:
        if id not in list(prior.index):
            tweet_text = f"NEW $MIR POLL ALERT [{id}]: {df.loc[id].title} ... #vote https://terra.mirror.finance/gov/poll/{id} $LUNA $ANC #terra"
            if len(tweet_text) > 140:
                tweet_text = f"NEW $MIR POLL ALERT [{id}]: {df.loc[id].title[:20]} ... #vote https://terra.mirror.finance/gov/poll/{id} $LUNA $ANC #terra"
            api.update_status(tweet_text)
            print(f"TWEET SENT --- {tweet_text}")

    # save latest poll data
    df.to_pickle("mirror_data.pkl")
    print(f"run complete {time.gmtime().tm_hour}:{time.gmtime().tm_min}:{time.gmtime().tm_sec}")

if __name__ == '__main__':
    schedule.every(1).hours.do(main)

    while True:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            print(f"{n} seconds until next run")
            time.sleep(n)
        schedule.run_pending()


# capture poll['id']
# check poll['status'] ['title'] ['link']
# if status changed from last time, tweet result
# if new poll id, tweet
# also add tweet when 24 hours from the end of a poll
    # or blocks to end
# tweet when close to quoroum
    # need total staked amount for this
# tweet live results when threshold met

# number of MIR for votes includes 6 sig figs so 1mm is 1000000000000

# df.to_pickle(filename) to save the file for later use
# pd.read_pickle(filename) to load it back
