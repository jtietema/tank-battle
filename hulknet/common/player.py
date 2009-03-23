class Player:
    def __init__(self, protocol):
        self.protocol = protocol
        self.currentGame = None
        self.name = None
        self.symbol = None

    def destroy(self):
        self.protocol = None

    def setError(self, id, msg):
        self.protocol.errorId = id
        self.protocol.errorMsg = msg