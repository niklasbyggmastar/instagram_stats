import requests
import json
from datetime import datetime
import plotly
import plotly.offline as py
import plotly.graph_objs as go
import numpy
import webbrowser
from config import Config

# TODO: Hide credentials
conf = Config()

plotly.tools.set_credentials_file(username=conf.USERNAME, api_key=conf.API_KEY)

client_id = conf.CLIENT_ID
redirect_uri = "http://localhost:8000"
authorize_url = "https://api.instagram.com/oauth/authorize/?client_id=" + client_id + "&redirect_uri=" + redirect_uri + "&response_type=token"
#webbrowser.open(authorize_url)

access_token = conf.ACCESS_TOKEN
api = "https://api.instagram.com/v1/users/self/?access_token=" +  access_token

username = ""
followers = 0
following = 0

stats_file = conf.HOST + "stats.json"
previous_data = {}


def main():
    global previous_data
    parseJson()
    previous_data = read_stats_file()

    latest_num_of_followers = previous_data['history'][0]['followers']
    latest_num_of_followings = previous_data['history'][0]['following']

    write_stats_file()

    print("\nWelcome " + username + "\n")
    print("* Followers now: " + str(followers))
    print("* Followers last time: " + str(latest_num_of_followers) + "\n")
    print("* Following now: " + str(following))
    print("* Following last time: " + str(latest_num_of_followings))

    create_graph()

    # New unfollows
    if latest_num_of_followers > followers:
        num_of_unfollows = latest_num_of_followers-followers
        if num_of_unfollows == 1:
            print("Someone has unfollowed you")
        elif num_of_unfollows > 1:
            print(str(num_of_unfollows) + ' have unfollowed you')

    # New followers
    elif latest_num_of_followers < followers:
        num_of_follows = followers-latest_num_of_followers
        if num_of_follows == 1:
            print("Someone started following you")
        elif num_of_follows > 1:
            print(str(num_of_follows) + ' have started following you')


def parseJson():
    global username, followers, following
    request = requests.get(api)
    data = json.loads(request.content)
    username = data['data']['username']
    followers = data['data']['counts']['followed_by']
    following = data['data']['counts']['follows']


def write_stats_file():
    with open(stats_file, 'w') as f:
        current_time = datetime.now()
        data = {
            'time': str(current_time),
            'followers': followers,
            'following': following
        }
        previous_data['history'].insert(0, data)
        json.dump(previous_data, f, indent=4)
        f.close()


def read_stats_file():
    with open(stats_file, 'r') as f:
        data = json.load(f)
        f.close()
        return data


def create_graph():
    history = previous_data['history']
    x_axis = []
    followers_y_axis = []
    followings_y_axis = []
    
    for score in history:
        x_axis.append(score['time'])
        followers_y_axis.append(score['followers'])
        followings_y_axis.append(score['following'])

    followers_line = go.Scatter(
        x = x_axis,
        y = followers_y_axis,
        name = "Followers"
    )

    followings_line = go.Scatter(
        x = x_axis,
        y = followings_y_axis,
        name = "Following"
    )

    py.plot([followers_line, followings_line], filename=conf.HOST + 'graph.html', auto_open=False)


#-------------------------
if __name__ == "__main__":
    main()