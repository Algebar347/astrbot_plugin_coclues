from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

@register("Coclues", "韵鱼", "跑团线索记录插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 数据库连接配置
        DATABASE_URI = 'mysql+mysqldb://root:Wys3032083430.@127.0.0.1/test'  # 替换为你的数据库信息
        self.engine = create_engine(DATABASE_URI)
        Base = declarative_base()
        # 定义模型
        class Clue(Base):
            __tablename__ = 'clues'
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            description = Column(String)
            status = Column(Enum('confirmed', 'doubtful'), default='doubtful')
            type = Column(Enum('person', 'location', 'item', 'event', 'timezone'), nullable=False)
        self.Clue = Clue
        # 创建数据库会话
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __del__(self):
        self.session.close()

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是一个 hello world 指令'''
        user_name = event.get_sender_name()
        message_str = event.message_str
        logger.info(event.get_messages())
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")

    @filter.command_group("猩红文档")
    def crimsonletters(self):
        pass

    @crimsonletters.command("help")
    async def help(self, event: AstrMessageEvent):
        yield event.plain_result("help")

    @crimsonletters.command("线索")
    async def clues(self, event: AstrMessageEvent):
        name = event.message_str

        def get_clues_by_name(name):
            """根据名称查询线索"""
            clues = self.session.query(self.Clue).filter(self.Clue.name == name).all()
            return clues

        found_clues = get_clues_by_name(name)
        if found_clues:
            for clue in found_clues:
                yield event.plain_result(f"线索: {clue.name}, 描述: {clue.description}, 状态: {clue.status}")
        else:
            yield event.plain_result("未找到相关线索。")
