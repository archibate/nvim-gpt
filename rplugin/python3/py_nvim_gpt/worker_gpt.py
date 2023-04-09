import os

from .worker import IWorker, WorkerFactory
from .io_tags import Done, UpdateParams, Reset, Rewind


class Worker_ChatGPT(IWorker):
    MODELS = [
        'gpt-3.5-turbo',
        'gpt-4',
        'gpt-4-32k',
        # 'text-davinci-003',
        # 'text-davinci-002',
        # 'code-davinci-002',
    ]

    PARAMS = dict(
            temperature = 1,
            top_p = 1,
            n = 1,
            presence_penalty = 0,
            frequency_penalty = 0,
            stream = False,
    )

    def _worker(self):
        print('ChatGPT started')
        if not os.environ.get('OPENAI_API_KEY'):
            print('* Please create the environment variable OPENAI_API_KEY with the API key')
            print('* See https://github.com/archibate/nvim-gpt/blob/main/README.md#for-chatgpt-users')
            raise RuntimeError('environment variable OPENAI_API_KEY not found (please follow instructions in https://github.com/archibate/nvim-gpt/blob/main/README.md#for-chatgpt-users)')

        import openai

        messages = []
        while True:
            print('ChatGPT waiting for question')
            question = self._questions.get()
            print('ChatGPT got question:')
            print(question)

            if isinstance(question, Reset):
                messages = []
                continue
            if isinstance(question, Rewind):
                if messages:
                    messages.pop()
                    if messages:
                        messages.pop()
                continue
            elif isinstance(question, UpdateParams):
                self._params = dict(question.params)
                continue

            messages.append({
                'role': 'user',
                'content': question,
            })

            print('ChatGPT starts request...')
            completion = openai.ChatCompletion.create(
                    model=self._model, messages=messages, **self._params)

            print('ChatGPT replies:')
            if self._params['n'] > 1 or not self._params['stream']:
                choices = completion.choices  # type: ignore
                if len(choices) > 1:
                    choices = sorted(choices, key=lambda s: s['index'])
                    response = ['({})\n'.format(i + 1) + choice.message.content for i, choice in enumerate(choices)]
                    response = '\n'.join(response)
                else:
                    response = choices[0].message.content
                print(response)
                messages.append({'role': 'assistant', 'content': response})
                self._answers.put(response)
                self._answers.put(Done())
            else:
                answer = ''
                for part in completion:
                    choices = part["choices"]  # type: ignore
                    assert len(choices) == 1
                    if 'message' not in choices[0]:
                        raise RuntimeError('no message found in {}'.format(choices))
                    resp = choices[0]["message"]["content"]
                    print(resp, end='', flush=True)
                    answer += resp
                    self._answers.put(resp)
                messages.append({'role': 'assistant', 'content': answer})
                self._answers.put(Done())


WorkerFactory.instance().register_worker_type('ChatGPT', Worker_ChatGPT)

__all__ = []
