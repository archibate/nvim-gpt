import json
import os

from .worker import IWorker, WorkerFactory
from .io_tags import Done, UpdateParams, Reset, Rewind


class Worker_BingAI(IWorker):
    MODELS = [
        'creative',
        'balanced',
        'precise',
    ]

    PARAMS = dict(
    )

    def _worker(self):
        print('BingAI started')
        from EdgeGPT import EdgeGPT
        from . import async_to_sync as sync

        cookies_path = '~/.bing-cookies.json'
        cookies_path = os.path.expanduser(cookies_path)
        if not os.path.exists(cookies_path):
            print('* Please create the file ~/.bing-cookies.json with Bing cookies')
            print('* See https://github.com/archibate/nvim-gpt/blob/main/README.md#for-bing-ai-users')
            raise RuntimeError('file ~/.bing-cookies.json not found (please follow instructions in https://github.com/archibate/nvim-gpt/blob/main/README.md#for-bing-ai-users)')
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
        bot = EdgeGPT.Chatbot(cookies=cookies)

        while True:
            print('BingAI waiting for question')
            question = self._questions.get()
            print('BingAI got question:')
            print(question)

            if isinstance(question, Reset):
                sync.function(bot.reset)
                continue
            if isinstance(question, Rewind):
                continue
            elif isinstance(question, UpdateParams):
                self._params = dict(question.params)
                continue

            answer = ''
            def callback(part):
                nonlocal answer
                if len(part):
                    print(part, end='', flush=True)
                    answer += part
                    self._answers.put(part)

            print('BingAI starts request...')
            style = getattr(EdgeGPT.ConversationStyle, self._model)
            sync.function(self._async_ask)(bot, question, style, callback)

            print('BingAI replies:')
            print(answer)
            self._answers.put(Done())

        # sync.function(bot.close)()

    @staticmethod
    async def _async_ask(bot, question, style, callback):
        wrote = 0
        async for final, response in bot.ask_stream(prompt=question, conversation_style=style):
            if not final:
                if len(response) < wrote:
                    callback('[Bing revoked their response]')
                callback(response[wrote:])
                wrote = len(response)


WorkerFactory.instance().register_worker_type('BingAI', Worker_BingAI)

__all__ = []
