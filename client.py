import time

from tank_battle.client.application import TankBattleClient
from tank_battle.client.factory import GameClientFactory

def run():
    client = TankBattleClient(GameClientFactory)
    last = time.time()
    client.connect('localhost',7777)
    while True:
        now = time.time()
        interval = now - last
        last = now
        client.update(interval)
        time.sleep(0.1)

if __name__ == '__main__':
    run()