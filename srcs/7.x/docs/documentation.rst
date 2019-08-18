스크립트 문서화
===============

.. currentmodule:: click

클릭을 쓰면 작성하는 명령행 도구의 문서화를 아주 쉽게 할 수 있다.
무엇보다 도움말 페이지를 자동으로 생성해 준다. 현재 글 배치 쪽은
조정이 불가능하지만 글 내용은 모두 변경 가능하다.

도움말
------

명령과 옵션에서 도움말 인자를 받는다. 그리고 명령에서는 함수
독스트링(docstring)을 적어 주면 그걸 자동으로 이용한다.

간단한 예:

.. click:example::

    @click.command()
    @click.option('--count', default=1, help='인사 횟수')
    @click.argument('name')
    def hello(count, name):
        """이 스크립트는 hello NAME을 COUNT 번 찍는다."""
        for x in range(count):
            click.echo('Hello %s!' % name)

그러면 다음처럼 된다.

.. click:run::

    invoke(hello, args=['--help'])

인자는 이런 식으로 문서화 할 수 없다. 이 경우에는 일반적인
유닉스 도구들의 관행을 따라서 꼭 필요한 곳에만 인자를 쓰고
도구 소개 문장에서 인자를 이름으로 지칭해서 설명하면 된다.

줄 바꿈 막기
------------

클릭의 기본 동작 방식은 터미널 폭에 맞춰 텍스트 줄을 바꾸는
것이다. 그런데 어떤 경우에는 이게 문제가 될 수 있다. 개행
위치가 중요한 코드 예시를 보일 때가 특히 그렇다.

이스케이프 표시 ``\b``\만 있는 행을 추가해 줘서 문단 단위로
줄 바꿈을 끌 수 있다. 도움말 내용에서는 그 행이 없어지고
줄 바꿈이 꺼지게 된다.

예:

.. click:example::

    @click.command()
    def cli():
        """첫 번째 문단.

        그리고 아주 긴 두 번째 문단이 이어지는데
        소스에서는 아주 일찍 줄이 바뀌지만 최종
        출력에서는 터미널 폭에 따라 줄이 바뀌는
        걸 볼 수 있다.

        \b
        줄 바꿈
        없는
        문단이다.

        그리고 이 문단에서는
        다시 줄 바꿈이 이뤄진다.
        """

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, args=['--help'])

.. _doc-meta-variables:

도움말 잘라내기
---------------

클릭은 함수 독스트링에서 명령 도움말을 얻는다. 하지만 이미
함수 인자 문서화에 독스트링을 이용하고 있다면 도움말 내용에
:param: 내지 :return: 행이 나오는 걸 보고 싶지는 않을 수 있다.

이스케이프 표시 ``\f``\를 쓰면 클릭이 그 표시 위치에서
도움말을 자른다.

예:

.. click:example::

    @click.command()
    @click.pass_context
    def cli(ctx):
        """첫 번째 문단.

        아주 긴 두 번째 문단인데
        개행이 제대로 돼 있지
        않지만 줄 바꿈이 이뤄질 것이다.
        \f

        :param click.core.Context ctx: 클릭 문맥.
        """

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, args=['--help'])


메타 변수
---------

옵션과 매개변수에서 ``metavar`` 인자를 받는데 이를 이용해
도움말 페이지의 메타 변수를 바꿀 수 있다. 매개변수 이름을
대문자로 하고 밑줄을 쓰는 게 기본 버전이지만 원한다면 다른
표기 방식을 쓸 수 있다. 모든 단계에서 조정이 가능하다.

.. click:example::

    @click.command(options_metavar='<options>')
    @click.option('--count', default=1, help='인사 횟수',
                  metavar='<int>')
    @click.argument('name', metavar='<name>')
    def hello(count, name):
        """이 스크립트는 <name>을 <int> 번 찍는다."""
        for x in range(count):
            click.echo('Hello %s!' % name)

그러면 다음처럼 된다.

.. click:run::

    invoke(hello, args=['--help'])


짧은 명령 도움말
----------------

명령들에는 짧은 도움말 문장이 생성된다. 기본적으로는 너무 길지만
않으면 명령 도움말 메시지의 첫 번째 문단을 쓴다. 이를 바꿀 수도
있다.

.. click:example::

    @click.group()
    def cli():
        """간단한 명령행 도구."""

    @cli.command('init', short_help='저장소 초기화')
    def init():
        """저장소를 초기화한다."""

    @cli.command('delete', short_help='저장소 삭제')
    def delete():
        """저장소를 삭제한다."""

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='repo.py')


도움말 동작 바꾸기
------------------

.. versionadded:: 2.0

도움말 매개변수는 클릭에서 아주 특별한 방식으로 구현돼 있다.
일반 매개변수들과 달리 클릭에서 모든 명령에 자동으로 추가해
주며 자동으로 충돌 해결을 수행해 준다. 기본 이름은
``--help``\이며 변경 가능하다. 명령 자체에서 같은 이름의
매개변수를 구현하면 더 이상 기본 도움말 매개변수를 받지
않는다. :attr:`~Context.help_option_names`\라는 문맥 설정을
이용해 도움말 매개변수의 이름을 바꿀 수 있다.

다음 예에서는 기본 매개변수를 ``--help``\만 쓰는 것에서
``-h`` 및 ``--help``\로 바꾼다.

.. click:example::

    CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

    @click.command(context_settings=CONTEXT_SETTINGS)
    def cli():
        pass

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, ['-h'])
