API
===

.. module:: click

모든 공개 클래스 및 함수들에 대한 전체 API 참조 문서이다.

데코레이터
----------

.. autofunction:: command

.. autofunction:: group

.. autofunction:: argument

.. autofunction:: option

.. autofunction:: password_option

.. autofunction:: confirmation_option

.. autofunction:: version_option

.. autofunction:: help_option

.. autofunction:: pass_context

.. autofunction:: pass_obj

.. autofunction:: make_pass_decorator

유틸리티
--------

.. autofunction:: echo

.. autofunction:: echo_via_pager

.. autofunction:: prompt

.. autofunction:: confirm

.. autofunction:: progressbar

.. autofunction:: clear

.. autofunction:: style

.. autofunction:: unstyle

.. autofunction:: secho

.. autofunction:: edit

.. autofunction:: launch

.. autofunction:: getchar

.. autofunction:: pause

.. autofunction:: get_terminal_size

.. autofunction:: get_binary_stream

.. autofunction:: get_text_stream

.. autofunction:: open_file

.. autofunction:: get_app_dir

.. autofunction:: format_filename

명령
----

.. autoclass:: BaseCommand
   :members:

.. autoclass:: Command
   :members:

.. autoclass:: MultiCommand
   :members:

.. autoclass:: Group
   :members:

.. autoclass:: CommandCollection
   :members:

매개변수
--------

.. autoclass:: Parameter
   :members:

.. autoclass:: Option

.. autoclass:: Argument

문맥
----

.. autoclass:: Context
   :members:

.. autofunction:: get_current_context

타입
----

.. autodata:: STRING

.. autodata:: INT

.. autodata:: FLOAT

.. autodata:: BOOL

.. autodata:: UUID

.. autodata:: UNPROCESSED

.. autoclass:: File

.. autoclass:: Path

.. autoclass:: Choice

.. autoclass:: IntRange

.. autoclass:: Tuple

.. autoclass:: ParamType
   :members:

예외
----

.. autoexception:: ClickException

.. autoexception:: Abort

.. autoexception:: UsageError

.. autoexception:: BadParameter

.. autoexception:: FileError

.. autoexception:: NoSuchOption

.. autoexception:: BadOptionUsage

.. autoexception:: BadArgumentUsage

서식
----

.. autoclass:: HelpFormatter
   :members:

.. autofunction:: wrap_text

파싱
----

.. autoclass:: OptionParser
   :members:

테스트
------

.. currentmodule:: click.testing

.. autoclass:: CliRunner
   :members:

.. autoclass:: Result
   :members:
