from Application import AbstractComponent, RootApplication
import random


class TestComponent(AbstractComponent):
    def __init__(self, root):
        super().__init__("Test", root)

        self.state['name'] = "NoName"
        self.actions['chooseNameAction'] = self.chooseNameAction
        self.mutations['updateNameMutation'] = self.updateNameMutation
        self.on('Test.chooseNameAction', self.onChooseNameAction)
        self.on('Test.updateNameMutation', self.onUpdateNameMutation)

    """
    On défini une méthode de choix d'un nom parmis un tableau de nom.
    """
    async def chooseNameAction(self, context, payload):
        choice = random.choice(payload.names)
        context.commit('Test.updateNameMutation', {'name': choice})

    """
    On défini une méthode qui permettra d'afficher le payload envoyé à
    la méthode de choix de nom.
    """
    def onChooseNameAction(self, context, payload):
        print('Action Choose Name Executed')
        print(f'Payload : {payload}')
        print('-----------------------------')

    """
    On défini la méthode de mutation qui permettra de changer le state
    """
    def updateNameMutation(self, states, payload):
        self.state['name'] = payload.name

    """
    On défini une méthode permettant de vérifier le payload de la mutation
    et de vérifier que le state à bien été muté.
    """
    def onUpdateNameMutation(self, context, payload):
        print('Mutation updateNameMutation executed')
        print(f'Payload : {payload}')
        print('-----------------------------')
        print('Actual State')
        print(self.state['name'])
        print('-----------------------------')


if __name__ == '__main__':
    app = RootApplication()
    app.use(TestComponent)

    i = 0

    # On exécute l'action plusieurs fois pour clairement voir les effets
    while i < 20:
        print(f'LOOP : {i}')
        app.dispatch_threaded('Test.chooseNameAction', {'names': ['marc', 'morgan', 'elie', 'mia']})
        i += 1
