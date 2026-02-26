from app import create_app
from app import db   # asegurate de importar db

app = create_app()



if __name__ == '__main__':
    app.run(debug=True)





