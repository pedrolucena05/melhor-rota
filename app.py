from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import networkx as nx
import json


con= 'mysql+pymysql://root:123456@localhost/db_t05'

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SQLALCHEMY_DATABASE_URI'] = str(con)

db = SQLAlchemy(app)
db.init_app(app)


class db_caminhao(db.Model):
    id= db.Column('id_caminhao', db.Integer, primary_key=True, autoincrement=True)
    cheio= db.Column('cheio',db.Integer)
    localizacao= db.Column('localizacao',db.Integer)
    def __repr__(self):
      return "id: {0} | cheio: {1} | localizacao: {2}".format(self.id, self.cheio, self.localizacao)
    
    def to_json(self):
        return {"id":self.id, "cheio":self.cheio, "localizacao":self.localizacao}

#Main
@app.route("/")
def home():
    return "<h1>Algoritmo Djkstra :o | Calcule a melhor rota para carga e descarga de caminhões</h1>"

#CRUD
#CREATE
@app.route("/adicionar/<cheio>/<localizacao>/",methods = ['GET', 'POST'])
def add(cheio=0, localizacao=0):
    retorno={"status": "Erro ao cadastrar o caminhao"}
    if request.method=='GET':
        cheio=int(cheio)
        localizacao=int(localizacao)
        caminhao= db_caminhao(cheio=cheio,localizacao=localizacao)
        db.session.add(caminhao)
        db.session.commit()
        retorno={"status": "Caminhao cadastrado"}
    return json.dumps(retorno, indent=4)

#CRUD
#READ
@app.route("/mostrar-frota/", methods = ['GET'])
def read():
    retorno = {"status": "erro ao mostar frota"}
    if request.method=='GET':
        listar= db_caminhao.query.all()
        formata=[]
        for i in listar:
            formata.append(i.to_json())
        retorno = {
            "frota": formata,
            "status": "sucesso"
        }
    return json.dumps(retorno, indent=4)


#CRUD
#UPDATE
@app.route("/editar-localizacao/<id>/<local>/",methods = ['GET'])
def update_localizacao(id = 0, local = 0):
    if request.method == 'GET':
        id= int(id)
        local= int(local)
        up_caminhao= db.session.query(db_caminhao).get(id)
        up_caminhao.localizacao=local
        db.session.commit()
        retorno= {
            "status": "Localização alterada com sucesso!"
        }
    return json.dumps(retorno, indent=4)

@app.route("/alterar-carga/<id>/",methods = ['GET'])
def alterar_carga(id=0):
    retorno= {
        "status": "erro ao alterar a carga"
    }
    if request.method=='GET':
        id=int(id)
        up_caminhao= db.session.query(db_caminhao).get(id)
        if(up_caminhao.cheio==1):
            up_caminhao.cheio=0
            db.session.commit()
        else:
            up_caminhao.cheio=1
            db.session.commit()
        retorno= {
            "status": "carga alterada com sucesso"
        } 
    return json.dumps(retorno)


#CRUD
#DELETE
@app.route("/excl/<id>/", methods = ['GET'])
def delete(id=0):
    retorno= {
        "status": "erro ao deletar o caminhao"
    }
    if request.method=='GET':
        id=int(id)
        del_caminhao=db.session.query(db_caminhao).get(id)
        db.session.delete(del_caminhao)
        db.session.commit()
        retorno= {
            "status": "caminhao foi deletado"
        }
    return json.dumps(retorno)
#fim do CRUD

#Algorithmos de Dijkstra
@app.route("/carregar-ou-descarregar/<id>/",methods =['GET'])
def carregar_prox(id=0):
    if request.method=='GET':
        caminhao=db.session.query(db_caminhao).get(id)
        if caminhao.cheio==1:
            rota1= dijkstra(caminhao.localizacao, 4)
            rota2= dijkstra(caminhao.localizacao, 5)
            rota3= dijkstra(caminhao.localizacao, 6)
            rota_final=rota1[0]
            menor=rota1[1]
            if rota2[1]<menor:
                rota_final=rota2[0]
                menor=rota2[1]
            if rota3[1]<menor:
                rota_final = rota3[0]
                menor=rota3[1] 
            return json.dumps(rota_final)
        else:
            rota1= dijkstra(caminhao.localizacao, 1)
            rota2= dijkstra(caminhao.localizacao, 2)
            rota3= dijkstra(caminhao.localizacao, 3)
            rota_final=rota1[0]
            menor=rota1[1]
            if rota2[1]<menor:
                rota_final=rota2[0]
                menor=rota2[1]
            if rota3[1]<menor:
                rota_final = rota3[0]
                menor=rota3[1] 
            return json.dumps(rota_final)


def dijkstra (onde_esta, destino):
    G= nx.Graph()
    e=[('1', '7', 200.0), ('7', '8', 200.0), ('7', '9', 120.0), ('9', '11', 250.0), ('9', '10', 200.0), 
    ('10', '4', 180.0), ('10', '11', 270.0), ('11', '13', 280.0), ('8', '12', 100.0), ('11', '13', 300.0), 
    ('13', '14', 250.0), ('14', '13', 210.0), ('14', '3', 130.0), ('14', '15', 250.0), ('13', '16', 250.0), 
    ('16', '15', 30.0), ('16', '17', 130.0), ('17', '5', 140.0), ('16', '18', 120.0), ('15', '19', 300.0), 
    ('18', '19', 170.0), ('18', '2', 160.0), ('19', '6', 100.0),
    ('7', '1', 200.0), ('8', '7', 200.0), ('9', '7', 120.0), ('11', '9', 250.0), ('10', '9', 200.0), 
    ('4', '10', 180.0), ('11', '10', 270.0), ('13', '11', 280.0), ('12', '8', 100.0), ('13', '11', 300.0), 
    ('3', '14', 130.0), ('15', '14', 250.0), ('16', '13', 250.0), 
    ('15', '16', 30.0), ('17', '16', 130.0), ('5', '17', 140.0), ('18', '16', 120.0), ('19', '15', 300.0), 
    ('19', '18', 170.0), ('2', '18', 160.0), ('6', '19', 100.0)]
    G.add_weighted_edges_from(e)
    rota= nx.dijkstra_path(G, str(onde_esta), str(destino))
    distancia=0
    for i in range(len(rota)-1):
        distancia += get_distance(rota[i],rota[i+1], e)
            
    return (rota, distancia)

def get_distance (pont_origem, pont_destino, e):
    for item in e:
        if (item[0]==pont_origem and item[1]==pont_destino):
            return item[2]
    return 0


if __name__ == "__main__":
    app.run(debug=True)
    

