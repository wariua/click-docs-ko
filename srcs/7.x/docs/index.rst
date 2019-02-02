.. rst-class:: hide-header

클릭을 클릭
===========

.. image:: _static/click-logo.png
    :align: center
    :scale: 50%
    :target: https://palletsprojects.com/p/click/

클릭(Click)은 꼭 필요한 코드만으로 아름다운 명령행 인터페이스를
조립할 수 있는 파이썬 패키지다. "Command Line Interface Creation Kit"를
줄인 이름이다. 폭넓은 설정이 가능하면서도 적절한 기본값이 갖춰져 있다.

명령행 도구 작성 작업을 빠르고 재밌게 만들면서도 원하는 CLI API를
구현할 수 없어서 좌절하는 일이 없도록 하는 걸 목표로 한다.

클릭에는 세 가지 특징이 있다.

-   마음대로 명령 계층 만들기
-   도움말 자동 생성
-   하위 모듈 런타임 적재 지원

다음은 간단한 클릭 프로그램 예시이다.

.. click:example::

    import click

    @click.command()
    @click.option('--count', default=1, help='인사 횟수.')
    @click.option('--name', prompt='이름',
                  help='인사를 받을 사람.')
    def hello(count, name):
        """NAME에게 총 COUNT 번 인사를 하는 간단한 프로그램"""
        for x in range(count):
            click.echo('Hello %s!' % name)

    if __name__ == '__main__':
        hello()

실행하면 다음과 같이 된다.

.. click:run::

    invoke(hello, ['--count=3'], prog_name='python hello.py', input='John\n')

자동으로 멋진 형식의 도움말을 만들어 준다.

.. click:run::

    invoke(hello, ['--help'], prog_name='python hello.py')

PyPI에서 바로 라이브러리를 받을 수 있다. ::

    pip install click

기본 문서
---------

라이브러리 사용 패턴 모두를 차례로 설명한다.

.. toctree::
   :maxdepth: 2

   why
   quickstart
   setuptools
   parameters
   options
   arguments
   commands
   prompts
   documentation
   complex
   advanced
   testing
   utils
   bashcomplete
   exceptions
   python3
   wincmd

API 참조 문서
-------------

특정 함수나 클래스, 메소드에 대한 내용을 찾는다면 여기를 보면 된다

.. toctree::
   :maxdepth: 2

   api

기타 페이지
-----------

.. toctree::
   :maxdepth: 2

   contrib
   changelog
   upgrading
   license
