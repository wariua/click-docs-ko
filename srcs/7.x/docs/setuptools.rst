.. _setuptools-integration:

setuptools 사용
===============

명령행 유틸리티를 작성할 때는 유닉스의 #!을 이용하는 것보다는
setuptools 배포 모듈로 작성하기를 권장한다.

왜 그래야 할까? 많은 이유가 있다.

1.  전통적 방식의 문제점 하나는 파이썬 인터프리터가 처음
    적재하는 모듈이 잘못된 이름을 가지게 된다는 것이다. 사소한
    문제처럼 들릴 수도 있겠지만 그로 인한 영향이 꽤 크다.

    첫 번째 모듈이 실제 이름으로 불리는 게 아니라 인터프리터에서
    이름을 ``__main__``\으로 바꾼다. 완벽하게 유효한 이름이기는
    하지만 그 때문에 어떤 다른 코드에서 그 모듈을 임포트 하려고
    하면 실제 이름으로 두 번째 임포트가 일어나게 되고 그래서
    느닷없이 코드가 두 번 임포트 된다.

2.  뭔가를 실행하는 게 모든 플랫폼에서 그렇게 간단하지는 않다.
    리눅스와 OS X에서는 파일 처음에 주석(``#!/usr/bin/env
    python``)을 추가하면 스크립트가 (실행 비트가 설정돼 있으면)
    실행 파일처럼 동작한다. 하지만 윈도우에서는 이게 안 된다.
    윈도우에서 파일 확장자에 인터프리터를 연계할 수 있기는
    하지만 (가령 ``.py`` 로 끝나는 파일이 모두 파이썬
    인터프리터를 통해 실행되게 할 수 있지만) 그러면 virtualenv
    안에서 그 스크립트를 사용하려고 할 때 문제가 생긴다.

    사실 virtualenv 안에서 스크립트를 실행하는 건 OS X와
    리눅스에서도 문제가 된다. 전통적 방식으로 올바른 파이썬
    인터프리터를 쓰려면 virtualenv 전체를 활성화시켜야 한다.
    별로 사용자 친화적이지 않다.

3.  스크립트가 파이썬 모듈일 때만 main 방식이 통한다. 응용이
    너무 커져서 패키지를 쓰고 싶어질 때가 되면 여러 문제들을
    만나게 된다.

도입
----

스크립트를 setuptools로 묶으려면 파이썬 패키지로 된 스크립트와
``setup.py`` 파일만 있으면 된다.

다음 같은 디렉터리 구조를 상상해 보자. ::

    yourscript.py
    setup.py

``yourscript.py`` 내용:

.. click:example::

    import click

    @click.command()
    def cli():
        """예시 스크립트."""
        click.echo('Hello World!')

``setup.py`` 내용::

    from setuptools import setup

    setup(
        name='yourscript',
        version='0.1',
        py_modules=['yourscript'],
        install_requires=[
            'Click',
        ],
        entry_points='''
            [console_scripts]
            yourscript=yourscript:cli
        ''',
    )

핵심은 ``entry_points`` 매개변수이다. ``console_scripts`` 아래의
각 행이 콘솔 스크립트 하나씩을 나타낸다. 등호(``=``) 앞의 부분은
생성할 스크립트 이름이고 뒷부분은 임포트 경로에 콜론(``:``)과
클릭 명령을 붙인 것이다.

이게 전부다.

스크립트 테스트
---------------

스크립트를 테스트 하기 위해 새 virtualenv를 만들어서 패키지를
설치해 볼 수 있다. ::

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install --editable .

그러면 명령이 사용 가능해진다.

.. click:run::

    invoke(cli, prog_name='yourscript')

패키지 형태 스크립트
--------------------

스크립트가 커져서 파이썬 패키지로 전환하려 할 때는 약간만
변경해 주면 된다. 디렉터리 구조가 다음처럼 바뀌었다고 하자. ::

    yourpackage/
        __init__.py
        main.py
        utils.py
        scripts/
            __init__.py
            yourscript.py

이 경우 ``setup.py``\에서 ``py_modules``\를 쓰는 대신 ``packages``\를
쓰고 setuptools의 자동 패키지 탐색 기능을 이용할 수 있다. 더불어
기타 패키지 데이터를 포함시키는 것도 권장한다.

바뀐 ``setup.py`` 내용은 다음과 같을 것이다. ::

    from setuptools import setup, find_packages

    setup(
        name='yourpackage',
        version='0.1',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'Click',
        ],
        entry_points='''
            [console_scripts]
            yourscript=yourpackage.scripts.yourscript:cli
        ''',
    )
