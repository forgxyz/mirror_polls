import pandas as pd
import json
import subprocess


def main():
    # run cli to get current polls data
    out = subprocess.run(['mirrorcli', 'query', 'gov', 'polls'], capture_output=True, text=True)

    # jsonify
    res = json.loads(out.stdout)

    # load into dataframe
    df = pd.DataFrame(res['polls'])
    df = df.set_index('id')

    # save latest poll data
    df.to_pickle("mirror_data.pkl")


if __name__ == '__main__':
    main()
