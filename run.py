from flask import render_template

from app import init_app
from flask import request

app = init_app()  # 创建app
from app import db
from app.models import Actors

@app.route('/',methods=['GET','POST'])
def start():
    print('hh')
    if request.method == 'GET':
        if request.args.get('actor_c_name'):
            print('hh1')
            name = request.args.get('actor_c_name')
            actors = db.session.query(Actors).filter(Actors.actor_c_name.like('%' + name + '%')).order_by(Actors.actor_c_name).all()
        else:
            actors = db.session.query(Actors).order_by(Actors.actor_c_name).all()
        db.session.close()
        for actor in actors:
            actor.actor_img = actor.actor_img.split('/')[-1]
        print('hh2')
        return render_template("start.html", Actors=actors)

if __name__ == '__main__':
    app.run()
