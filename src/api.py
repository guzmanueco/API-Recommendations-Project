from bottle import route, run, get, post, request
import random
from mongo import CollConection
import bson


@post('/add')
def add(chat_num, user_num, line_x):
    print(dict(request.forms))
    chat=request.forms.get(chat_num)
    user=request.forms.get(user_num)
    line=request.forms.get(line_x)


    return {
        "inserted_doc": str(coll.addLine(chat, user, line))}


@get("/chiste/<tipo>")
def demo2(tipo):
    print(f"un chiste de {tipo}")
    if tipo == "chiquito":
        return {
            "chiste": "Van dos soldados en una moto y no se cae ninguno porque van soldados"
        }
    elif tipo == "eugenio":
        return {
            "chiste": "Saben aquell que diu...."
        }
    else:
        return {
            "chiste": "No puedorrr!!"
        }




coll=CollConection('Prueba','datamad1019')
run(host='0.0.0.0', port=8080)