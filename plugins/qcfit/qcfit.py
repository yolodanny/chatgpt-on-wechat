# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from .summary import QcSummary


@plugins.register(
    name="QcFit",
    desire_priority=100,
    hidden=True,
    desc="A plugin for qcfit",
    version="0.1",
    author="xiao",
)
class Qcfit(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Qcfit] inited")

    def on_handle_context(self, e_context: EventContext):
        context = e_context['context']
        if context.type not in [
            ContextType.SHARING,
        ]:
            return

        if (context.type == ContextType.SHARING):
            _send_info(e_context, "正在为你加速生成摘要，请稍后")
            res = QcSummary().summary_url(context.content)
            logger.info(res)
            _send_info(e_context, res)
            return

    
def _send_info(e_context: EventContext, content: str):
    reply = Reply(ReplyType.TEXT, content)
    channel = e_context["channel"]
    channel.send(reply, e_context["context"])
