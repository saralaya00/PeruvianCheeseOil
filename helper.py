import json
import random
import requests
from bs4 import BeautifulSoup

def scrape_daily_problem(source):
  source_name = source['name']

  if source_name == "codechef":
    url = source['problem_source']
    plain = requests.get(url).text
    soup = BeautifulSoup(plain, "html.parser")

    div = soup.find('div', {'class': 'l-card-11'})
    problem_title = div.find('p', {'class': 'm-card-11_head-2'}).text
    anchor = div.find('a', {'class': 'm-button-1'})
    link = url + anchor.get('href')

    return {
      "problem_title" : problem_title,
      "link" : link,
      "msg" : source["msg_template"].format(problem_title = problem_title, link = link)
    }

  elif source_name == "codeforces":
    current_index = ["A", "B"] # codeforces index to identify difficulty of the problem, lower is easier
    with open('codeforces_problemset.json') as fp:
      problemset = json.load(fp)

    filtered_problems = list(filter(lambda obj: obj['index'] in current_index, problemset['result']['problems']))
    
    # Problem Schema: https://codeforces.com/apiHelp/objects#Problem
    # {'contestId': 612, 'index': 'A', 'name': 'The Text Splitting', 'type': 'PROGRAMMING', 'rating': 1300, 'tags': ['brute force', 'implementation', 'strings']}
    problem = random.choice(filtered_problems)
    problem_title = problem['name'] 
    link = f"{source['problem_dest']}/{problem['contestId']}/{problem['index']}"

    return {
      "problem_title" : problem_title,
      "link" : link,
      "msg" : source["msg_template"].format(problem_title = problem_title, link = link, tags = problem['tags'])
    }
    
  else:
    return {
      "problem_title" : "Bad Implementation",
      "link" : "Bad Implementation",
      "msg" : "Bad Implementation"
    }

# For Testing 
# out = scrape_daily_problem(
#   {
#     "name" : "codeforces",
#     "problem_source" : "https://codeforces.com/api/problemset.problems", # API Source where we can get the problemset json (manually used for now)
#     "problem_dest" : "https://codeforces.com/problemset/problem",
#     "msg_template" : "**Codeforces - Random daily**\nTitle: {problem_title}\nTags: ||{tags}||\n{link}"
#   }
# )
# print(out['msg'])