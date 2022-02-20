import logging
from flask import Flask
from threading import Thread

# Ping this server periodically with
# https://uptimerobot.com
app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
  log = logging.getLogger('werkzeug')
  log.disabled = True 
  t = Thread(target=run)
  t.start()