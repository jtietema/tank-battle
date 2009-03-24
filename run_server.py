from tank_battle.server.server import TankBattleServer

def run():
    port = 7777
    delay = 0.02
    server = TankBattleServer(port)
    server.run(delay)

if __name__ == '__main__':
    run()