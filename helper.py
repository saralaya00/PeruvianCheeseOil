import json
import markdown
import random
import requests
from bs4 import BeautifulSoup

def get_codechef_daily(source):
  url = source['problem_source']
  plain = requests.get(url).text
  soup = BeautifulSoup(plain, "html.parser")

  # Identifies html tags and creates the message
  div = soup.find('div', {'class': 'l-card-11'})
  problem_title = div.find('p', {'class': 'm-card-11_head-2'}).text
  anchor = div.find('a', {'class': 'm-button-1'})
  link = url + anchor.get('href')

  return {
    "problem_title" : problem_title,
    "link" : link,
    "msg" : source["msg_template"].format(problem_title = problem_title, link = link)
  }

def get_codeforces_random(source):
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

def get_leetcode_random(source):
  url = source['problem_source']

  # Problem list markdown Schema: https://github.com/fishercoder1534/Leetcode/blob/master/README.md
  # | #    |      Title     |   Solutions   | Video  | Difficulty  | Tag
  # | 1910 |[Remove All Occurrences of a Substring](https://leetcode.com/problems/remove-all-occurrences-of-a-substring/)|[Solution](../master/src/main/java/com/fishercoder/solutions/_1904.java) |[:tv:](https://youtube...)|Medium|String|
  rawMD = requests.get(url).text.split('\n')

  # A boolean that identifies that a '## Algorithms' header was identified so we can start to parse the required markdown table
  isAlgo = False 
  problemset = []
  for line in rawMD:
    if "## Shell" in line:
      break
    if "## Algorithms" in line:
      isAlgo = True
      continue
    if isAlgo:
      if (
        len(line) == 0
        or '## Database' in line # '## Database' section markdown table which can also be parsed
        or 'Title' and 'Solution' in line
        or '|---' in line
      ):
        # ignore headers and empty lines  
        continue
      
      # On_line.split('|'): ['', ' 1910 ', '[Remove All Occurrences of a Substring](https://leetcode.com/problems/remove-all-occurrences-of-a-substring/)', '[Solution](../master/src/main/java/com/fishercoder/solutions/_1904.java) ', '[:tv:](https://youtube...)', 'Medium', 'String', '']
      problemset.append(line.split('|'))

  problem = random.choice(problemset)
  plain = markdown.markdown(problem[2].strip())
  soup = BeautifulSoup(plain, "html.parser")
  anchor = soup.find('a')

  problem_num = problem[1].strip()
  problem_title = anchor.contents[0]
  link = anchor.get('href')
  difficulty = problem[5].strip()

  msg = source["msg_template"].format(problem_num = problem_num, problem_title = problem_title, difficulty = difficulty, link = link)
  return {
    "problem_title" : problem_title,
    "link" : link,
    "msg" : msg
  }

def scrape_daily_problem(source):
  source_name = source['name']
  if source_name == "codechef":
    return get_codechef_daily(source)

  elif source_name == "codeforces":
    return get_codeforces_random(source)

  elif source_name == "leetcode":
    return get_leetcode_random(source)

  else:
    return {
      "problem_title" : "Bad Implementation",
      "link" : "Bad Implementation",
      "msg" : "Bad Implementation"
    }

# # For Testing 
# out = scrape_daily_problem(
#   {
#     "name" : "codeforces",
#     "problem_source" : "https://codeforces.com/api/problemset.problems", # API Source where we can get the problemset json (manually used for now)
#     "problem_dest" : "https://codeforces.com/problemset/problem",
#     "msg_template" : "**Codeforces - Random daily**\n{problem_title}\n||{tags}||\n{link}"
#   }
# )
# print(out['msg'])