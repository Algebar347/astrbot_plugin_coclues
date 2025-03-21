from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from sqlalchemy import create_engine, Column, Integer, String, Date, Time
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

@register("Coclues", "韵鱼", "跑团线索记录插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    def init_database(self):
        # 数据库连接配置
        DATABASE_URI = 'mysql+mysqldb://root:Wys3032083430.@127.0.0.1/crimsonletters'  # 替换为你的数据库信息
        self.engine = create_engine(DATABASE_URI)
        Base = declarative_base()
        # 定义模型
        # 通用线索
        class Clue(Base):
            __tablename__ = 'clues'
            id = Column(Integer, primary_key=True)
            name = Column(String(255), nullable=False)
            description = Column(String)
            status = Column(Enum('confirmed', 'doubtful'), default='doubtful')
            type = Column(Enum('location', 'item', 'event'), nullable=False)
        self.Clue = Clue
        # 人物
        class Character(Base):
            __tablename__ = 'characters'
            id = Column(Integer, primary_key=True)
            name = Column(String(50), nullable=False)
            full_name = Column(String(100))
            role = Column(String)
            clue1 = Column(String)
            clue2 = Column(String)
            clue3 = Column(String)
            relationships1 = relationship("Relationship", foreign_keys="[Relationship.character1_id]")
            relationships2 = relationship("Relationship", foreign_keys="[Relationship.character2_id]")
        self.Character = Character
        #人物关系
        class Relationship(Base):
            __tablename__ = 'relationships'
            id = Column(Integer, primary_key=True)
            character1_id = Column(Integer, ForeignKey('characters.id', ondelete='CASCADE'))
            character2_id = Column(Integer, ForeignKey('characters.id', ondelete='CASCADE'))
            relation = Column(String)
            status = Column(String)
        self.Relationship = Relationship
        #时间线
        class Timeline(Base):
            __tablename__ = 'timeline'
            id = Column(Integer, primary_key=True)
            event_date = Column(Date, nullable=False)
            event_time = Column(Time)
            description = Column(String, nullable=False)
        self.Timeline = Timeline

        # 创建数据库会话
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    @filter.command_group("猩红文档")
    def crimsonletters(self):
        pass

    @crimsonletters.command("help")
    async def help(self, event: AstrMessageEvent):
        # 返回帮助信息
        instructions = "欢迎使用韵鱼のcoc跑团线索记录插件，我们正在玩：《猩红文档》！\n使用命令查询：\n" \
        "/猩红文档 线索 <关键词>\n" \
        "/猩红文档 人物 <人物名>\n" \
        "若需列出同一类型的全部线索，使用命令：\n" \
        "/猩红文档 时间线\n" \
        "/猩红文档 物品\n" \
        "/猩红文档 角色"
        yield event.plain_result(f"{instructions}")

    @crimsonletters.command("线索")
    async def clues(self, event: AstrMessageEvent):
        self.init_database()
        name = event.get_message_str().replace("猩红文档 线索", "", 1).strip()
        def get_clues_by_name(name):
            """根据名称查询线索"""
            clues = self.session.query(self.Clue).filter(self.Clue.name == name).all()
            return clues

        found_clues = get_clues_by_name(name)
        if found_clues:
            for clue in found_clues:
                yield event.plain_result(f"线索: {clue.name}\n 描述: {clue.description}\n 状态: {clue.status}")
        else:
            yield event.plain_result("未找到相关线索。")

    @crimsonletters.command("人物")
    async def characters(self, event: AstrMessageEvent):
        self.init_database()
        name = event.get_message_str().replace("猩红文档 人物", "", 1).strip()
        def get_characters_by_name(name):
            """根据名称查询人物"""
            characters = self.session.query(self.Character).filter(self.Character.name == name).all()
            return characters

        found_characters = get_characters_by_name(name)
        if found_characters:
            character_info="\n".join([i[0] for i in found_characters])
            yield event.plain_result(f"人物: {character_info}")
        else:
            found_allcharacters = self.session.query(self.Character.name).all()
            allcharacters = "\n".join([i[0] for i in found_allcharacters])
            yield event.plain_result(f"未找到相关人物。\n 已解锁的人物列表：\n{allcharacters}")

    @crimsonletters.command("时间线")
    async def timeline(self, event: AstrMessageEvent):
        self.init_database()
        found_timeline = self.session.query(self.Timeline).all()
        if found_timeline:
            timeline="\n".join([f"时间: {i.event_date} {i.event_time}\n 事件: {i.description}" for i in found_timeline])
            yield event.plain_result(f"时间线：\n{timeline}")
        else:
            yield event.plain_result("出错了，未找到相关时间线。")

    @crimsonletters.command("物品")
    async def objects(self, event: AstrMessageEvent):
        self.init_database()
        def get_objects_by_name(name):
            """根据名称查询物品"""
            objects = self.session.query(self.Clue).filter(self.Clue.name == name, self.Clue.type == 'item').all()
            return objects

        found_objects = get_objects_by_name(name)
        if found_objects:
            for obj in found_objects:
                yield event.plain_result(f"物品: {obj.name}, 描述: {obj.description}, 状态: {obj.status}")
        else:
            yield event.plain_result("未找到相关物品。")
