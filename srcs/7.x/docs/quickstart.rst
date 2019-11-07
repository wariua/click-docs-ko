빨리 해 보기
============

.. currentmodule:: click

PyPI에서 바로 라이브러리를 받을 수 있다. ::

    pip install click

:ref:`virtualenv` 안에 설치하기를 강력히 권한다.

.. _virtualenv:

virtualenv
----------

클릭 응용을 개발할 때 아마 virtualenv를 쓰고 싶을 것이다.

virtualenv가 해결해 주는 문제가 뭘까? 아마 작성한 클릭 스크립트뿐
아니라 다른 프로젝트들에도 쓰고 싶을 것이다. 프로젝트가
늘어날수록 파이썬을 여러 버전을 써서, 또는 적어도 파이썬
라이브러리들을 여러 버전을 써 가며 작업하게 될 가능성이 높다.
그리고 우리가 인정해야 할 현실은 라이브러리들에서 하위 호환성을
깨는 경우가 꽤 많다는 것이고, 제대로 된 응용에 의존성이 없을
가능성은 낮다는 것이다. 그렇다면 작성 중인 둘 이상의 프로젝트에서
의존성이 충돌한다면 어떻게 해야 할까?

virtualenv가 있다! virtualenv를 쓰면 각 프로젝트마다 하나씩 여러
개의 파이썬 설치 환경을 만들 수 있다. 실제로 파이썬 사본을 따로
설치하는 건 아니고 똑똑한 어떤 방식으로 프로젝트 환경들을 격리해
준다. virtualenv가 어떻게 도는지 살펴보자.

맥 OS X나 리눅스에서라면 아마 다음 두 명령 중 하나가 동작할 것이다. ::

    $ sudo easy_install virtualenv

더 좋은 방식::

    $ sudo pip install virtualenv

아마 이 중 한 명령으로 시스템에 virtualenv가 설치될 것이다. 또
어쩌면 패키지 관리자에 있을 수도 있다. 우분투를 쓴다면 이렇게
해 보자. ::

    $ sudo apt-get install python-virtualenv

윈도우를 쓴다면 (또는 위 방법 어느 것도 안 된다면) 먼저 ``pip`` 를
설치해야 한다. 자세한 내용은 `pip 설치하기`_\를 보라. 설치를
마쳤으면 위의 ``pip`` 명령을 앞의 `sudo`\를 빼고 실행하면 된다.

.. _pip 설치하기: https://pip.readthedocs.io/en/latest/installing.html

virtualenv를 설치했으면 셸을 하나 띄워서 새 환경을 만들자.
보통 프로젝트 폴더를 만들고 그 안에 `venv` 폴더를 만든다. ::

    $ mkdir myproject
    $ cd myproject
    $ virtualenv venv
    New python executable in venv/bin/python
    Installing setuptools, pip............done.

이제 프로젝트 작업을 하고 싶을 때마다 해당 환경을 활성화해
주기만 하면 된다. OS X와 리눅스에서는 다음처럼 한다. ::

    $ . venv/bin/activate

윈도우 사용자라면 다음 명령을 쓰면 된다. ::

    $ venv\scripts\activate

어느 방식을 통해서든 이제 그 virtualenv를 사용하게 됐다.
(셸 프롬프트가 활성 환경을 보여 주도록 바뀐 걸 알 수 있다.)

그리고 실제 세계로 돌아가고 싶으면 다음 명령을 쓰면 된다. ::

    $ deactivate

그러면 셸 프롬프트가 이전처럼 익숙한 모습으로 돌아간다.

그럼 계속 진행해 보자. 다음 명령을 입력해서 새로 만든 virtualenv
안에서 Click이 작동하게 하자. ::

    $ pip install Click

몇 초만 기다리면 준비가 끝난다.

스크린캐스트와 예시
-------------------

클릭의 기본 API와 간단한 응용 제작 방법을 보여 주는
스크린캐스트가 있다. 하위 명령이 있는 명령들을 만드는
방법도 볼 수 있다.

*   `클릭으로 명령행 응용 만들기
    <https://www.youtube.com/watch?v=kNke39OZ2k0>`_

이 문서뿐 아니라 GitHub 저장소에서도 readme 파일까지 있는
클릭 예시 응용들을 찾을 수 있다.

*   ``inout``: `파일 입력과 출력
    <https://github.com/pallets/click/tree/master/examples/inout>`_
*   ``naval``: `docopt의 naval 예시 포팅
    <https://github.com/pallets/click/tree/master/examples/naval>`_
*   ``aliases``: `명령 별칭 예시
    <https://github.com/pallets/click/tree/master/examples/aliases>`_
*   ``repo``: `Git/Mercurial 방식 명령행 인터페이스
    <https://github.com/pallets/click/tree/master/examples/repo>`_
*   ``complex``: `플러그인을 적재하는 복잡한 예시
    <https://github.com/pallets/click/tree/master/examples/complex>`_
*   ``validation``: `매개변수 검증 예시
    <https://github.com/pallets/click/tree/master/examples/validation>`_
*   ``colors``: `Colorama ANSI 색상 지원
    <https://github.com/pallets/click/tree/master/examples/colors>`_
*   ``termui``: `터미널 UI 함수 시연
    <https://github.com/pallets/click/tree/master/examples/termui>`_
*   ``imagepipe``: `연쇄 명령 시연
    <https://github.com/pallets/click/tree/master/examples/imagepipe>`_

기본 개념 - 명령 만들기
-----------------------

클릭의 기본은 데코레이터를 통해 명령을 선언하는 것이다. 고급 사용
방식을 위한 데코레이터 아닌 인터페이스가 내부적으로 있기는 하지만
위쪽 층위에서 쓰는 건 권장하지 않는다.

:func:`click.command`\를 통해 꾸며 주면 함수가 클릭 명령행 도구가
된다. 간단하게는 어떤 함수를 이 데코레이터로 꾸며 주기만 하면
호출 가능한 스크립트가 된다.

.. click:example::

    import click

    @click.command()
    def hello():
        click.echo('Hello World!')

이렇게 하면 데코레이터가 함수를 :class:`Command`\로 변환하고,
그걸 다음처럼 호출할 수 있다. ::

    if __name__ == '__main__':
        hello()

다음처럼 실행할 수 있다.

.. click:run::

    invoke(hello, args=[], prog_name='python hello.py')

도움말 페이지도 있다.

.. click:run::

    invoke(hello, args=['--help'], prog_name='python hello.py')

echo
----

왜 이 예시에서는 표준 :func:`print` 함수 대신 :func:`echo`\를
쓸까? 답은 클릭에서 파이썬 2와 파이썬 3 모두를 같은 방식으로
지원하려 하고 환경이 잘못 구성된 경우에도 아주 견고하게
동작하려 하기 때문이다. 모든 게 완전히 고장난 경우에도
적어도 기본적인 수준에서는 동작이 되게 하려고 한다.

즉 터미널이 잘못 구성돼 있는 경우에 :func:`echo` 함수는
:exc:`UnicodeError`\로 죽는 대신 뭔가 오류 수정을 한다.

추가로 클릭 2.0부터는 echo 함수에서 ANSI 색상도 잘 지원한다.
출력 스트림이 파일이면 자동으로 ANSI 코드를 제거해 주고
colorama가 제공되면 윈도우에서도 ANSI 색상이 동작하게 된다.
참고로 파이썬 2에서는 :func:`echo` 함수가 bytearray의
색상 코드 정보를 파싱 하지 않는다. 자세한 내용은
:ref:`ansi-colors` 절 참고.

이런 게 필요치 않다면 `print()` 구성체/함수를 쓸 수도 있다.

명령 계층화
-----------

명령들을 :class:`Group` 타입인 다른 명령에 갖다 붙일 수 있다.
이를 이용하면 스크립트들을 마음대로 계층 구조로 만들 수 있다.
예를 들어 다음은 데이터베이스 관리를 위한 두 가지 명령을
구현한 스크립트다.

.. click:example::

    @click.group()
    def cli():
        pass

    @click.command()
    def initdb():
        click.echo('Initialized the database')

    @click.command()
    def dropdb():
        click.echo('Dropped the database')

    cli.add_command(initdb)
    cli.add_command(dropdb)

보다시피 :func:`group` 데코레이터는 :func:`command` 데코레이터와
비슷하게 동작하되 대신 :class:`Group` 객체를 생성한다. 그 객체에
:meth:`Group.add_command`\로 하위 명령들을 붙일 수 있다.

스크립트를 간단하게 만들기 위해 :meth:`Group.command` 데코레이터를
대신 써서 자동으로 명령을 붙여서 만드는 것도 가능하다. 위
스크립트를 다음처럼 작성할 수 있다.

.. click:example::

    @click.group()
    def cli():
        pass

    @cli.command()
    def initdb():
        click.echo('Initialized the database')

    @cli.command()
    def dropdb():
        click.echo('Dropped the database')

그러고 나서는 setuptools 진입 지점이나 다른 호출점에서
:class:`Group`\을 호출하게 된다. ::

    if __name__ == '__main__':
        cli()

매개변수 추가하기
-----------------

매개변수를 추가하려면 :func:`option` 및 :func:`argument` 데코레이터를
쓰면 된다.

.. click:example::

    @click.command()
    @click.option('--count', default=1, help='인사 횟수')
    @click.argument('name')
    def hello(count, name):
        for x in range(count):
            click.echo('Hello %s!' % name)

그러면 다음처럼 된다.

.. click:run::

    invoke(hello, args=['--help'], prog_name='python hello.py')

.. _switching-to-setuptools:

setuptools로 바꾸기
-------------------

지금까지 작성한 코드에는 파일 끝에 ``if __name__ == '__main__':``
비슷한 블록이 있다. 전통적으로 단독형 파이썬 파일의 형태가 그렇다.
클릭을 쓰면서 계속 그렇게 할 수도 있지만 setuptools를 사용하는
더 나은 방법도 있다.

그렇게 하는 주된 이유 두 가지를 꼽을 수 있다. (다른 이유도 많다.)

첫 번째는 setuptools가 윈도우를 위한 실행 가능 래퍼를 자동으로
생성해 주기 때문에 명령행 유틸리티가 윈도우에서도 동작한다는 점이다.

두 번째 이유는 유닉스에서 virtualenv를 활성화하지 않아도 setuptools
스크립트가 virtualenv와 동작한다는 점이다. 이는 매우 유용한
개념으로, 덕분에 스크립트와 모든 필요 모듈들을 virtualenv로
묶어서 배포할 수 있다.

클릭은 그렇게 동작할 준비가 완벽하게 돼 있으며 실제로 이 문서
나머지에서는 setuptools를 통해 응용을 작성한다고 가정할 것이다.

예시들에서 setuptools 사용을 가정하고 있으므로 나머지 부분을
읽기 전에 :ref:`setuptools-integration` 장을 들여다보기를
강력히 권한다.
