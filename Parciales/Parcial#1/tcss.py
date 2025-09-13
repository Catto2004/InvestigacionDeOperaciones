# tcss.py
CSS = """
Screen {
    layout: horizontal;
}

#BarraSuperior {
    height: 1;
    color: yellow;
    dock: top;
}

#PanelPrincipal {
    height: 1fr;
}

#PanelIzquierdo {
    width: 40%;
    border: solid gray;
    padding: 1;
}

#PanelDerecho {
    width: 60%;
    border: solid gray;
    padding: 1;
}

#InputFunObj, #InputRestriccion {
    margin: 1;
}

#MaxMin {
    margin: 1;
    width: 3;
}

Button.-error {
    background: red;
    color: white;
}

"""
