import pandas as pd
import json
import tweepy
import schedule
import subprocess
import time

# run on pi with nohup python3 -u mirror.py > logs/output.log &


def main():
    # load twitter api info
    with open('creds.json') as f:
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

    try:
        # jsonify
        res = json.loads(out.stdout)
    
    
        # load into dataframe
        df = pd.DataFrame(res['polls'])
        df = df.set_index('id')

        # load previous polls data
        prior = pd.read_pickle('data/mirror_data.pkl')

        # check for any new information
        for id in df.index:
            if id not in list(prior.index):
                tweet_text = f"NEW MIRROR POLL! {df.loc[id].title} ... #vote on {id}: http://mirrorprotocol.app/#/gov/poll/{id} $MIR $LUNA #terra"
                if len(tweet_text) > 280:
                    tweet_text = f"NEW MIRROR POLL! {df.loc[id].title[:50]} ... #vote on {id}: http://mirrorprotocol.app/#/gov/poll/{id} $MIR $LUNA #terra"
                api.update_status(tweet_text)
                print(f"TWEET SENT --- {tweet_text}")

        # save latest poll data
        df.to_pickle("data/mirror_data.pkl")
        print(f"run complete {time.gmtime().tm_mon}/{time.gmtime().tm_mday} {time.gmtime().tm_hour}:{time.gmtime().tm_min}:{time.gmtime().tm_sec}")

    except ValueError:
        print("JSON Error")


if __name__ == '__main__':
    schedule.every(1).hours.do(main)

    while True:
        n = schedule.idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()
