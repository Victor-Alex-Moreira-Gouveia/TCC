from flask import Flask
from app.routes import health, usuarios, noticias, ongs, ajuda

def create_app():
    app = Flask(__name__)
    
    # Registrar blueprints (rotas)
    app.register_blueprint(health.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(noticias.bp)
    app.register_blueprint(ongs.bp)
    app.register_blueprint(ajuda.bp)
    
    return app
