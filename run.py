from app import init_app

app = init_app()  # 创建app


@app.route('/')
def hello_world():
    return 'Hello World! run'

if __name__ == '__main__':
    app.run()
