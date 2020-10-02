from Components import AbstractComponent


class MainComponent(AbstractComponent):
    def __init__(self, root_app):
        super(MainComponent, self).__init__("Main", root_app)

        self.state.__setattr__("last_hello", "None")
        self.actions.__setattr__("sayHello", self.sayHello)
        self.mutations.__setattr__("updateLastHello", self.updateLastHello)

    async def sayHello(self, context, payload):
        print(f'Hello {payload.name}')
        context.commit('Main.updateLastHello', payload.name)

    def updateLastHello(self, states, value):
        states.Main.last_hello = value
