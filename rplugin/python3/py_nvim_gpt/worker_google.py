from .worker import IWorker, WorkerFactory
from .io_tags import Done, UpdateParams, Reset, Rewind


class Worker_Google(IWorker):
    MODELS = [
        'google-search',
    ]

    PARAMS = dict(
            num_results = 10,
            sleep_interval = 0,
            timeout = 5,
            lang = 'en',
            format = '\n# {title}\n- {url}\n\n{desc}\n',
    )

    def _worker(self):
        print('Google started')
        import googlesearch

        while True:
            print('Google waiting for question')
            question = self._questions.get()
            print('Google got question:')
            print(question)

            if isinstance(question, Reset):
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

            term = question
            print('Google starts searching...')
            params = dict(self._params)
            format = params.pop('format')
            for result in googlesearch.search(term, advanced=True, **params):
                print('Google got one result:')
                print(result)
                answer = format.format(url=result.url, title=result.title, desc=result.description)
                callback(answer)

            self._answers.put(Done())

        # sync.function(bot.close)()

    @staticmethod
    async def _async_ask(bot, question, style, callback):
        wrote = 0
        async for final, response in bot.ask_stream(prompt=question, conversation_style=style):
            if not final:
                callback(response[wrote:])
                wrote = len(response)


WorkerFactory.instance().register_worker_type('Google', Worker_Google)

__all__ = []
