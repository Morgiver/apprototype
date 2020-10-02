from Components import AbstractComponent


class LoggerComponent(AbstractComponent):
    def __init__(self, root_app):
        super().__init__("Logger", root_app)

        self.subscribe('Main.updateLastHello', self.logAllHello)

    def logAllHello(self, value):
        print(f'Someone just say hello to : {value}')
