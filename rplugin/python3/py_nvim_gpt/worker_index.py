import os
import traceback

from .worker import IWorker, WorkerFactory
from .io_tags import Done, UpdateParams, Reset, Rewind


class Worker_GPTIndex(IWorker):
    MODELS = [
        'gpt-index',
    ]

    PARAMS = dict(
            temperature = 1,
            top_p = 1,
            n = 1,
            presence_penalty = 0,
            frequency_penalty = 0,
            stream = False,
    )

    @classmethod
    def _apply_patches(cls):
        if hasattr(cls, '_patches_applied'):
            return

        import nest_asyncio
        nest_asyncio.apply()

        import logging
        import sys

        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        cls._patches_applied = True
        print('GPTIndex patches applied')

    def _worker(self):
        print('GPTIndex started')
        if not os.environ.get('OPENAI_API_KEY'):
            print('* Please create the environment variable OPENAI_API_KEY with the API key')
            print('* See https://github.com/archibate/nvim-gpt/blob/main/README.md#for-chatgpt-users')
            raise RuntimeError('environment variable OPENAI_API_KEY not found (please follow instructions in https://github.com/archibate/nvim-gpt/blob/main/README.md#for-chatgpt-users)')

        self._apply_patches()
        self._index = None

        messages = []
        while True:
            print('GPTIndex waiting for question')
            question = self._questions.get()
            print('GPTIndex got question:')
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

            print('GPTIndex starts request...')
            if question.startswith('%index_'):
                command = question[len('%index_'):]
                response = self._index_command(command)
            else:
                response = self._index_query(question)

            print('GPTIndex replies:')
            print(response)
            messages.append({'role': 'assistant', 'content': response})
            self._answers.put(response)
            self._answers.put(Done())

    def _index_query(self, question):
        if self._index is None:
            return 'Please first specify the documentation folder you want to index by asking:\n%index_dir /path/to/your/docs\nSee %index_help for more details.'
        else:
            return self._index.query(question)

    def _index_command(self, command):
        import gpt_index

        if not hasattr(self, '_index_method'):
            self._index_method = gpt_index.GPTSimpleVectorIndex

        if command.startswith('dir '):
            spec = command[len('dir '):].strip()
            spec = spec.split(' --include=')
            path = spec[0] if len(spec) else ''
            exts = spec[1] if len(spec) > 1 else ''
            exts = exts.strip().split(',')
            if not path:
                return 'Please specify the documentation folder to read from'
            try:
                docs = gpt_index.SimpleDirectoryReader(input_dir=path, recursive=True, required_exts=exts).load_data()
            except:
                traceback.print_exc()
                return 'Error while reading directory: {}\n{}'.format(path, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for directory: {}\n{}'.format(path, traceback.format_exc())
            return 'Index built successfully for directory: {}'.format(path)

        if command.startswith('files '):
            path = command[len('files '):].strip()
            if not path:
                return 'Please specify the text file(s) to read from'
            try:
                files = path.split()
                docs = gpt_index.SimpleDirectoryReader(input_files=files).load_data()
            except:
                traceback.print_exc()
                return 'Error while reading text file(s): {}\n{}'.format(path, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for text file(s): {}\n{}'.format(path, traceback.format_exc())
            return 'Index built successfully for text file(s): {}'.format(path)

        if command.startswith('web '):
            url = command[len('web '):].strip()
            if not url:
                return 'Please specify the url(s) of the website to read from'
            try:
                urls = url.split()
                docs = gpt_index.TrafilaturaWebReader().load_data(urls)
            except:
                traceback.print_exc()
                return 'Error while reading web url(s): {}\n{}'.format(url, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for web url(s): {}\n{}'.format(url, traceback.format_exc())
            return 'Index built successfully for web url(s): {}'.format(url)

        if command.startswith('wikipedia '):
            page = command[len('wikipedia '):].strip()
            if not page:
                return 'Please specify the wikipedia page(s) to read from'
            try:
                pages = page.split()
                docs = gpt_index.WikipediaReader().load_data(pages)
            except:
                traceback.print_exc()
                return 'Error while reading wikipedia page(s): {}\n{}'.format(page, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for wikipedia page(s): {}\n{}'.format(page, traceback.format_exc())
            return 'Index built successfully for wikipedia page(s): {}'.format(page)

        if command.startswith('discord '):
            channel = command[len('discord '):].strip()
            if not channel:
                return 'Please specify the discord channel id(s) to read from'
            try:
                channels = channel.split()
                docs = gpt_index.DiscordReader().load_data(channels)
            except:
                traceback.print_exc()
                return 'Error while reading discord channel(s): {}\n{}'.format(channel, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for discord channel(s): {}\n{}'.format(channel, traceback.format_exc())
            return 'Index built successfully for discord channel(s): {}'.format(channel)

        if command.startswith('notion '):
            page = command[len('notion '):].strip()
            try:
                pages = page.split()
                docs = gpt_index.NotionPageReader().load_data(pages)
            except:
                traceback.print_exc()
                return 'Error while reading notion page(s): {}\n{}'.format(page, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for notion page(s): {}\n{}'.format(page, traceback.format_exc())
            return 'Index built successfully for notion page(s): {}'.format(page)

        if command.startswith('github '):
            spec = command[len('github '):].strip()
            spec = spec.split(' --exclude=')
            owner_repo = spec[0] if len(spec) else ''
            ignore_file_extensions = spec[1] if len(spec) > 1 else ''
            ignore_file_extensions = ignore_file_extensions.strip().split(',')
            if not owner_repo or not owner_repo.count('/') == 1:
                return 'Please specify the GitHub repository to read from in the format: owner/repo'
            try:
                owner, repo = owner_repo.split('/')
                docs = gpt_index.GithubRepositoryReader(owner, repo, ignore_file_extensions=ignore_file_extensions).load_data()
            except:
                traceback.print_exc()
                return 'Error while reading GitHub repository: {}\n{}'.format(owner_repo, traceback.format_exc())
            try:
                self._index = self._index_method.from_documents(docs)
            except:
                traceback.print_exc()
                return 'Error while building index for Github repository: {}\n{}'.format(owner_repo, traceback.format_exc())
            return 'Index built successfully for Github repository: {}'.format(owner_repo)

        if command.startswith('method '):
            available_methods = [
                'GPTSimpleVectorIndex',
                'GPTSimpleKeywordTableIndex',
                'GPTVectorStoreIndex',
                'GPTListIndex',
                'GPTTreeIndex',
                'GPTKeywordTableIndex',
                'GPTEmptyIndex',
            ]
            method = command[len('load '):].strip()
            if not method:
                return 'Please specify index method to use\nAvailable methods are: {}'.format(', '.join(available_methods))
            if method not in available_methods:
                return 'Unknown index method: {}\nAvailable methods are: {}'.format(method, ', '.join(available_methods))
            self._index_method = getattr(gpt_index, method, gpt_index.GPTSimpleVectorIndex)
            return 'Successfully updated index method to: {}'.format(method)

        if command.startswith('load '):
            path = command[len('load '):].strip()
            if not path:
                return 'Please specify index file path to load from'
            try:
                self._index = self._index_method.load_from_disk(path)
            except:
                traceback.print_exc()
                return 'Error while loading index from index file: {}\n{}'.format(path, traceback.format_exc())
            else:
                return 'Index loaded successfully from index file: {}'.format(path)

        if command.startswith('save '):
            path = command[len('save '):].strip()
            if not path:
                return 'Please specify index file path to save'
            if self._index is None:
                return 'No index built yet, please use %index_dir to build first'
            try:
                self._index.save_to_disk(path)
            except:
                traceback.print_exc()
                return 'Error while saving index to index file: {}\n{}'.format(path, traceback.format_exc())
            else:
                return 'Index saved successfully to index file: {}'.format(path)

        if command.startswith('help'):
            return '''%index_help - Show this help message.
%index_dir my-docs-folder - Build index for text files in this folder. It should contains only plain text files, no binary files. Reads recursively.
%index_dir my-docs-folder --include=.txt,.md - Build index for text files in this folder. But only include .txt or .md files. Useful when the folder contains many unrelated binary files.
%index_files file1.txt file2.txt - build index for a specified list of text files. Space separated.
%index_urls a.com/url1.txt b.com/url2.txt - Build index for a specified list of web URLs. Space separated.
%index_wikipedia wikipage1 wikipage2 - Build index for a specified list of wikipedia pages. Space separated.
%index_discord channelId1 channelId2 - Build index for a specified list of discord channels. Space separated. Needs to set the environment variable DISCORD_TOKEN.
%index_notion pageId1 pageId2 - Build index for a specified list of notion pages. Space separated. Needs to set the environment variable NOTION_INTEGRATION_TOKEN.
%index_notion - Build index for all notion pages available with your NOTION_INTEGRATION_TOKEN.
%index_github owner/repo --exclude=.png,.jpg - Build index for a GitHub repository owner/repo, files with extension name .png and .jpg are ignored. Needs to set the environment variable GITHUB_TOKEN.
%index_method GPTSimpleVectorIndex - Use alternative index method to use. Type %index_method for a list of available methods. The default method is GPTSimpleVectorIndex.
%index_save docs-index.json - Save current loaded index to the json file for future use. Method needs to be matched.
%index_load docs-index.json - Load previously saved index json file for reuse. Method needs to be matched.
<question> - Ask any question based on the indexed text files, after index loaded.
'''

        return 'Unrecognized index command: {}\nType %index_help for help'.format(command)


WorkerFactory.instance().register_worker_type('GPTIndex', Worker_GPTIndex)

__all__ = []
