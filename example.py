
from AbstractApplication import *


class TestComponent(AbstractComponent):
    def __init__(self, root):
        self.data = {
            "test": "Prout"
        }

        super().__init__("Test", root)

    def testaction_action(self, context, payload):
        context.commit('Test.testmutation', {})
        return "Pouet"

    def testgetter_getter(self):
        return f'{self.state.test} Test Getter'

    def testmutation_mutation(self, context, payload):
        context.states.Test.test = "Pouet"

    def testaction_action_listener(self, context, payload):
        print('Test Action Listener')
        print(f'{self.testgetter}')

    def testmutation_mutation_listener(self, context, payload):
        pass


class TestListenComponent(AbstractComponent):
    def __init__(self, root):
        self.data = {}

        super().__init__("TestListen", root)

    def testaction_action_listener(self, context, payload):
        print('Test Action Listener in TestListenComponent')

    def testmutation_mutation_listener(self, context, payload):
        print('Test Mutation Listener in TestListenComponent')


class Application(AbstractApplication):
    def __init__(self):
        super().__init__()

        self.use(TestComponent)
        self.use(TestListenComponent)


app = Application()
print(app.threaded_dispatch('Test.testaction', {}))
