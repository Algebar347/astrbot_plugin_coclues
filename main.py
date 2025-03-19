from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


@register("Coclues", "韵鱼", "跑团线索记录插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息


    @filter.command_group("猩红文档")   # 模组名称
    def crimsonletters(self):
        pass
    @crimsonletters.command("help") # 给出线索的索引
    async def help(self, event: AstrMessageEvent):
        yield event.plain_result("help")
    @crimsonletters.command("线索")
    async def clues(self, event: AstrMessageEvent):
        name= event.message_str
        # 数据库连接配置
        DATABASE_URI = 'mysql+mysqldb://root@84.235.248.49/test'  # 替换为你的数据库信息
        engine = create_engine(DATABASE_URI)

        Base = declarative_base()

        # 定义模型
        class Clue(Base):
            __tablename__ = 'test'

            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            description = Column(String)
            status = Column(Enum('confirmed', 'doubtful'), default='confirmedl')
            type = Column(Enum('person', 'location', 'item', 'event', 'timezone'), nullable=False)

        # 创建数据库会话
        Session = sessionmaker(bind=engine)
        session = Session()

        def get_clues_by_name(name):
            """根据名称查询线索"""
            clues = session.query(Clue).filter(Clue.name == name).all()
            return clues

        found_clues = get_clues_by_name(name)
        if found_clues:
            for clue in found_clues:
                yield event.plain_result(f"线索: {clue.name}, 描述: {clue.description}, 状态: {clue.status}")
        else:
            yield event.plain_result("未找到相关线索。")
        session.close()