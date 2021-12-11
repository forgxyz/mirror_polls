import pandas as pd
import json
import subprocess
import time

out = subprocess.run(['mirrorcli', 'query', 'gov', 'polls'], capture_output=True, text=True)

res = json.loads(out.stdout)


# load into dataframe
df = pd.DataFrame(res['polls'])
df = df.set_index('id')

prior = pd.read_pickle('data/mirror_data_mac.pkl')

# check for any new information
for id in df.index:
    if id not in list(prior.index):
        tweet_text = f"NEW $MIR POLL ALERT [{id}]: {df.loc[id].title} ... #vote http://mirrorprotocol.app/#/gov/poll/{id} $LUNA $ANC #terra"
        if len(tweet_text) > 140:
            tweet_text = f"NEW $MIR POLL ALERT [{id}]: {df.loc[id].title[:20]} ... #vote http://mirrorprotocol.app/#/gov/poll/{id} $LUNA $ANC #terra"
        print(f"TWEET MESSAGE --- {tweet_text}")

df.to_pickle("data/mirror_data_mac.pkl")
