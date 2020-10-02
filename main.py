from Application import *


app = Application(sys.argv)
app.load_components(['Main', 'Logger'])
app.dispatch('Main.sayHello', {'name': 'Morgiver'})
