import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger


@plugins.register(name="search_movies",
                  desc="search_movies插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class search_movies(Plugin):
    content = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f""
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        if self.content.startswith("搜电影"):
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            
            reply = Reply()
            result = self.search_movies()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS


    def search_movies(self):
        self.content = self.content[4:]
        url = "https://lj.sgai.cc/maren-master/baidu.php/?"
        params = f"text={self.content}"
        headers = {'Content-Type': "application/x-www-form-urlencoded",
                'User-Agent': 'My User Agent 1.0'}
        try:
            response = requests.get(url=url, params=params, headers=headers)
            json_data = response.json()
            if json_data.get('code',None) == 200 and json_data.get('list',None):
                data = json_data['list'][:10]
                logger.info(json_data)
                text = ("🔍为您搜索到以下资源：\n"
                        "--------------------")
                i = 0
                while i < len(data):
                    line = f"\n【{i+1}】:{data[i]['title']}\n🔗链接:{data[i]['url']}"
                    text+=line
                    i+=1
                return text
            else:
                text = "❌未搜索到相关资源"
                logger.error(f"搜索资源接口返回参数错误:{json_data}")
                return text
        except Exception as e:
            logger.error(f"搜索资源接口抛出异常:{e}")
                
        logger.error("所有接口都挂了,无法获取")
        return None
