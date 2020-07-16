import redis
class BaseConfig(object):
    #session配置
    # SESSION_TYPE = 'redis'  # session类型为redis
    # SESSION_KEY_PREFIX = 'session:'  # 保存到session中的值的前缀
    # SESSION_PERMANENT = True  # 如果设置为False，则关闭浏览器session就失效。
    # SESSION_USE_SIGNER = False  # 是否对发送到浏览器上 session:cookie值进行加密
    # SESSION_REDIS= redis.Redis(host='10.1.210.33', port='6379')
    #数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/farsystem?charset=utf8"
    SQLALCHEMY_POOL_SIZE = 10    #数据库连接池的大小。默认值 5
    SQLALCHEMY_POOL_TIMEOUT = 30  # 指定数据库连接池的超时时间。默认是 10
    SQLALCHEMY_POOL_RECYCLE = -1
    SQLALCHEMY_MAX_OVERFLOW = 3  # 控制在连接池达到最大值后可以创建的连接数。当这些额外的连接回收到连接池后将会被断开和抛弃
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 追踪对象的修改并且发送信号


class ProductionConfig(BaseConfig):
    """
    生产配置文件
    """
    pass


class DevelopmentConfig(BaseConfig):
    """
    开发配置文件
    """
    pass


class TestingConfig(BaseConfig):
    """
    测试配置文件
    """
    pass