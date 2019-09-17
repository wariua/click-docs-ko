유틸리티
========

.. currentmodule:: click

클릭에서는 인자 파싱 및 처리를 다루기 위한 것 외에도 명령행 도구
작성에 유용한 보조 기능들을 많이 제공한다.


stdout으로 출력하기
-------------------

가장 눈에 띄는 건 :func:`echo` 함수인데, 여러 면에서 파이썬의
``print`` 문 내지 함수와 비슷하게 동작한다. 주된 차이는
파이썬 2와 3에서 똑같이 동작하고, 잘못 구성된 출력 스트림을
똑똑하게 탐지하며, 절대 실패하지 않는다는 (파이썬 3 제외.
자세한 내용은 :ref:`python3-limitations` 참고) 점이다.

예::

    import click

    click.echo('Hello World!')

무엇보다 중요한 건 유니코드와 이진 데이터를 모두 찍을 수 있다는
점이다. 파이썬의 내장 ``print`` 함수로는 아무 바이트나 출력할 수
없다. 한편으로 끝에 개행을 기본적으로 찍는데, 막으려면
``nl=False``\를 주면 된다. ::

    click.echo(b'\xe2\x98\x83', nl=False)

또한 :func:`echo`\에서는 stdout 및 stderr로 연결된 똑똑한
클릭 내부의 출력 스트림을 이용한다. 그래서 윈도우 콘솔에서
유니코드 출력을 지원한다. 즉 `click.echo`\을 사용하기만
한다면 유니코드 문자를 출력할 수 있다는 거다. (표시될 수
있는 문자와 관련해 기본 폰트에 일부 제약이 있기는 하다.)
이 기능은 클릭 6.0에서 추가됐다.

.. versionadded:: 6.0

이제 윈도우에서 출력 스트림을 에뮬레이션 해서 별도 API를
통하면 윈도 콘솔에 유니코드를 찍는 걸 지원한다. 자세한 내용은
:doc:`wincmd` 참고.

.. versionadded:: 3.0

클릭 3.0부터는 ``err=True``\만 주면 표준 오류로도 간단히
출력할 수 있다. ::

    click.echo('Hello World!', err=True)


.. _ansi-colors:

ANSI 색상
---------

.. versionadded:: 2.0

클릭 2.0부터 :func:`echo` 함수에 ANSI 색상 및 스타일을 다룰 수
있는 기능이 추가됐다. 참고로 윈도우에서는 `colorama`_\가 설치돼
있는 경우에만 이 기능을 사용할 수 있다. 설치가 돼 있으면 ANSI
코드를 똑똑하게 처리해 준다. 참고로 파이썬 2에서는 echo 함수가
bytearray의 색상 코드 정보를 파싱 하지 않는다.

크게 다음처럼 동작한다.

-   스트림이 터미널에 연결돼 있지 않으면 클릭의 :func:`echo`
    함수가 자동으로 ANSI 색상 코드를 벗겨 낸다.
-   윈도우에서는 :func:`echo` 함수가 알아서 터미널에 연결해서
    ANSI 코드를 터미널 API 호출로 변환해 준다. 즉 윈도우에서도
    다른 운영 체제와 마찬가지로 색상이 동작하게 된다.

`colorama` 지원 관련 참고: 클릭에서 자동으로 `colorama`\가 있는지
탐지해서 이용한다. ``colorama.init()``\을 *호출하지 말자*.

`colorama`\를 설치하려면 다음 명령을 실행하면 된다. ::

    $ pip install colorama

문자열 스타일을 바꾸려면 :func:`style` 함수를 쓰면 된다. ::

    import click

    click.echo(click.style('Hello World!', fg='green'))
    click.echo(click.style('Some more text', bg='blue', fg='white'))
    click.echo(click.style('ATTENTION', blink=True, bold=True))

:func:`echo`\와 :func:`style`\을 조합하는 대신 :func:`secho`
함수를 한 번 호출하는 것도 가능하다. ::

    click.secho('Hello World!', fg='green')
    click.secho('Some more text', bg='blue', fg='white')
    click.secho('ATTENTION', blink=True, bold=True)


.. _colorama: https://pypi.org/project/colorama/

페이저 지원
-----------

어떤 경우에는 터미널에 긴 내용을 보여 주면서 사용자가 스크롤을
할 수 있게 하고 싶을 수 있다. :func:`echo_via_pager` 함수를
쓰면 되는데, 이 함수는 :func:`echo`\와 비슷하게 동작하되
항상 stdout으로, 그리고 가능하면 페이저를 통해서 쓴다.

예:

.. click:example::

    @click.command()
    def less():
        click.echo_via_pager('\n'.join('Line %d' % idx
                                       for idx in range(200)))

내용이 많아서 페이저를 쓰고 싶은데 모든 내용을 미리 생성하는 건 시간이 많이 걸릴 것 같다면 문자열 대신 제너레이터를 (즉 제너레이터 함수를) 줄 수 있다.

.. click:example::
    def _generate_output():
        for idx in range(50000):
            yield "Line %d\n" % idx

    @click.command()
    def less():
        click.echo_via_pager(_generate_output())


화면 비우기
-----------

.. versionadded:: 2.0

터미널 화면을 비우려면 클릭 2.0부터 제공되는 :func:`clear` 함수를
사용하면 된다. 이름처럼 동작한다. 즉 플랫폼과 상관없이 보이는
화면 전체를 비워 준다.

::

    import click
    click.clear()


터미널에서 문자 얻기
--------------------

.. versionadded:: 2.0

보통 터미널에서 입력을 읽을 때는 표준 입력에서 읽어 들이게 된다.
하지만 그건 버퍼링 입력이고 행이 종결돼야 내용이 나오게 된다.
어떤 경우에는 그렇게 하는 대신 개별 문자를 바로바로 읽고 싶을
수 있다.

이를 위해 클릭에서 :func:`getchar` 함수를 제공하는데, 터미널
버퍼에서 문자 하나를 읽어서 유니코드 문자로 반환한다.

참고로 이 함수는 stdin이 파이프이거나 한 경우에도 항상 터미널에서
읽는다.

예::

    import click

    click.echo('Continue? [yn] ', nl=False)
    c = click.getchar()
    click.echo()
    if c == 'y':
        click.echo('We will go on')
    elif c == 'n':
        click.echo('Abort!')
    else:
        click.echo('Invalid input :(')

참고로 이렇게 하면 입력을 있는 그대로 읽어 들이며, 그래서 방향 키
같은 게 플랫폼별 이스케이프 형식으로 찍히게 된다. 유일하게 처리를
하는 문제가 ``^C``\와 ``^D``\인데, 각각 키보드 인터럽트와 파일 끝
예외로 바뀐다. 이렇게 하는 이유는 안 그러면 미처 생각을 못 해서
제대로 끝낼 수 없는 스크립트를 만들게 되기 십상이기 때문이다.


키 입력 기다리기
----------------

.. versionadded:: 2.0

사용자가 키보드의 아무 키를 누를 때까지 실행을 정지하는 게 유용할
때가 있다. 특히 윈도우에서 유용한데, ``cmd.exe``\가 기본적으로
명령 실행을 마친 후 기다리지 않고 바로 창을 닫기 때문이다.

클릭에서는 :func:`pause` 함수를 쓰면 된다. 이 함수는 (변경 가능한)
짧은 메시지를 터미널에 표시하고서 사용자가 키를 누를 때까지
기다린다. 더불어 스크립트가 대화형으로 돌고 있는 게 아닌 경우에는
NOP(빈 연산)이 된다.

예::

    import click
    click.pause()


편집기 띄우기
-------------

.. versionadded:: 2.0

클릭에선 :func:`edit`\를 통해 자동으로 편집기를 띄울 수 있다.
사용자에게 여러 행으로 된 입력을 요청할 때 아주 유용하다.
사용자가 지정한 편집기가 있으면 그걸 자동으로 열고, 없으면
적당한 기본값을 쓰게 된다. 사용자가 저장 없이 편집기를 닫으면
반환 값이 `None`\이고 아니면 입력한 텍스트이다.

사용례::

    import click

    def get_commit_message():
        MARKER = '# Everything below is ignored\n'
        message = click.edit('\n\n' + MARKER)
        if message is not None:
            return message.split(MARKER, 1)[0].rstrip('\n')

또는 파일명을 지정해서 그 파일에 대해 편집기를 띄우도록 쓸
수도 있다. 그 경우에는 반환 값이 항상 `None`\이다.

사용례::

    import click
    click.edit(filename='/etc/passwd')


응용 띄우기
-----------

.. versionadded:: 2.0

클릭에선 :func:`launch`\를 통해 응용을 띄울 수 있다. 이를 이용해
어떤 URL이나 파일 타입에 연계된 기본 응용을 열 수 있다. 예를 들면
이를 이용해 웹 브라우저나 그림 뷰어를 띄울 수 있다. 더불어 파일
관리자를 열면서 지정한 파일이 자동으로 선택돼 있게 수 있다.

사용례::

    click.launch("https://click.palletsprojects.com/")
    click.launch("/my/downloaded/file.txt", locate=True)


파일명 찍기
-----------

파일명이 유니코드가 아닐 수도 있기 때문에 서식 문자열에 사용하기가
좀 까다로울 수 있다. 일반적으로 파이썬 2에서 더 간단한데,
바이트들을 ``print`` 함수로 stdout에 그냥 쓸 수 있기 때문이다.
하지만 파이썬 3에서는 항상 유니코드로 해야 한다.

이를 위해 클릭에는 :func:`format_filename` 함수가 있다.
최선을 다해 파일명을 유니코드로 변환해 주며 절대 실패하지
않는다. 그래서 그 파일명을 유니코드 문자열 맥락에 사용할 수
있게 해 준다.

예::

    click.echo('Path: %s' % click.format_filename(b'foo.txt'))


표준 스트림
-----------

명령행 도구에서는 입력 스트림과 출력 스트림에 잘 접근하는 게
아주 중요하다. 파이썬에서 기본적으로 ``sys.stdout`` 등을 통해
스트림에 접근할 수 있지만 아쉽게도 2.x와 3.x 간에 API 차이가
있으며 특히 유니코드 및 이진 데이터에 스트림이 반응하는 방식이
다르다.

이 때문에 클릭에는 :func:`get_binary_stream` 및
:func:`get_text_stream` 함수가 있는데, 상이한 파이썬 버전과
다양한 터미널 구성에서도 일관성 있는 결과를 내놓는다.

결론은 이 함수들이 항상 잘 동작하는 스트림 객체를 반환해
준다는 것이다. (파이썬 3의 아주 특이한 경우 제외.
:ref:`python3-limitations` 참고.)

예::

    import click

    stdin_text = click.get_text_stream('stdin')
    stdout_binary = click.get_binary_stream('stdout')

.. versionadded:: 6.0

이제 클릭은 윈도우에서 출력 스트림을 에뮬레이션 해서 별도
API를 통해 윈도우 콘솔로 유니코드를 찍을 수 있다. 자세한
내용은 :doc:`wincmd` 참고.


똑똑한 파일 열기
----------------

.. versionadded:: 3.0

클릭 3.0부터 :class:`File` 타입의 파일 여는 로직을
:func:`open_file` 함수를 통해서도 이용할 수 있다. 다른 파일들뿐
아니라 stdin/stdout도 똑똑하게 열어 준다.

예::

    import click

    stdout = click.open_file('-', 'w')
    test_file = click.open_file('test.txt', 'w')

stdin이나 stdout이 반환되는 경우 그 반환 값이 특별한 파일로
감싸져 있어서 문맥 관리자에서 파일이 닫히지 않도록 한다.
그 때문에 표준 스트림 처리가 투명해져서 언제나 다음처럼
쓸 수 있게 된다. ::

    with click.open_file(filename, 'w') as f:
        f.write('Hello World!\n')


응용 폴더 찾기
--------------

.. versionadded:: 2.0

응용에서 자기 설정 파일을 열고 싶을 때가 빈번히 있다. 하지만
운영 체제에서는 각자의 표준에 따라 각기 다른 위치에 설정
파일들을 저장한다. 클릭에서 제공하는 :func:`get_app_dir`
함수는 OS에 따라서 응용의 사용자별 설정 파일에 가장 적합한
위치를 반환한다.

사용례::

    import os
    import click
    import ConfigParser

    APP_NAME = 'My Application'

    def read_config():
        cfg = os.path.join(click.get_app_dir(APP_NAME), 'config.ini')
        parser = ConfigParser.RawConfigParser()
        parser.read([cfg])
        rv = {}
        for section in parser.sections():
            for key, value in parser.items(section):
                rv['%s.%s' % (section, key)] = value
        return rv


진행 막대 보여 주기
-------------------

.. versionadded:: 2.0

명령행 스크립트에서 많은 양의 데이터를 처리해야 하는데 걸릴
시간과 관련해 진행 상태를 사용자에게 빨리 보여 주고 싶을
때가 있다. 클릭에서는 :func:`progressbar` 함수를 통해
간단한 진행 막대를 표시할 수 있도록 한다.

기본적인 사용법은 아주 간단하다. 동작을 수행하려는 이터러블이
있으면 된다. 이터러블의 각 항목에 대해서 처리에 얼마간의 시간이
걸릴 수 있다. 가령 다음과 같은 루프가 있다고 하자. ::

    for user in all_the_users_to_process:
        modify_the_user(user)

이걸 가지고 자동으로 진행 막대가 갱신되게 하려면 코드를
다음처럼 바꿔 주기만 하면 된다. ::

    import click

    with click.progressbar(all_the_users_to_process) as bar:
        for user in bar:
            modify_the_user(user)

그러면 클릭에서 자동으로 진행 막대를 터미널에 표시하고 남은
시간을 계산해 준다. 남은 시간 계산을 위해선 이터러블에
길이가 있어야 한다. 이터러블에는 길이가 없지만 길이를 알고
있다면 명시적으로 알려 줄 수 있다. ::

    with click.progressbar(all_the_users_to_process,
                           length=number_of_users) as bar:
        for user in bar:
            modify_the_user(user)

또 다른 유용한 기능은 진행 막대에 레이블을 붙이는 것이다.
진행 막대 앞에 나오게 된다. ::

    with click.progressbar(all_the_users_to_process,
                           label='Modifying user accounts',
                           length=number_of_users) as bar:
        for user in bar:
            modify_the_user(user)

때로는 외부 이터레이터를 순회하면서 불규칙적으로 진행 막대를
진행시켜야 한다. 그렇게 하려면 (이터레이터 없이) 길이를
지정하고서 반환 값을 직접 순회하는 대신 update 메소드를
사용하면 된다. ::

    with click.progressbar(length=total_size,
                           label='Unzipping archive') as bar:
        for archive in zip_file:
            archive.extract()
            bar.update(archive.size)
