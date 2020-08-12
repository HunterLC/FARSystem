from flask import render_template

from app import init_app
from flask import request

from app.views.actor import get_frequent_cooperation_by_id

app = init_app()  # 创建app


@app.route('/',methods=['GET','POST'])
def login():
    return render_template("login.html",errors="")

if __name__ == '__main__':
    app.run()
