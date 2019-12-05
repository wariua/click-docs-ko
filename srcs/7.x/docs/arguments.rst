.. _arguments:

인자
====

.. currentmodule:: click

인자는 :ref:`옵션 <options>`\과 비슷하게 동작하되 위치가 정해져
있다. 그리고 그 문법적 특성 때문에 옵션의 기능 중 일부만 지원한다.
또한 클릭에서는 도움말 페이지가 복잡해지는 걸 피하기 위해
인자 설명을 표시하지 않으므로 원한다면 직접 적어 줘야 한다.

기본 인자
---------

가장 기본적인 옵션은 값 한 개로 된 단순 문자열 인자다. 타입을
주지 않으면 기본값의 타입을 쓰며, 기본값을 주지 않으면 타입이
:data:`STRING`\이라고 상정한다.

예:

.. click:example::

    @click.command()
    @click.argument('filename')
    def touch(filename):
        click.echo(filename)

그러면 다음처럼 된다.

.. click:run::

    invoke(touch, args=['foo.txt'])

가변 개수 인자
--------------

두 번째로 흔한 방식은 가변 개수 인자로, 정해진 수의 (또는 무제한의)
인자를 받는다. ``nargs`` 매개변수로 조절할 수 있다. ``-1``\로
설정하면 무제한으로 인자를 받는다.

값은 튜플로 전달된다. 참고로 ``nargs=-1``\로 설정하면 모든 인자를
먹게 되므로 한 인자만 그렇게 설정할 수 있다.

예:

.. click:example::

    @click.command()
    @click.argument('src', nargs=-1)
    @click.argument('dst', nargs=1)
    def copy(src, dst):
        for fn in src:
            click.echo('move %s to folder %s' % (fn, dst))

그러면 다음처럼 된다.

.. click:run::

    invoke(copy, args=['foo.txt', 'bar.txt', 'my_folder'])

응용을 이렇게 작성하면 된다는 게 아니다. 왜냐면 위 예에서
인자들이 문자열로 정의돼 있기 때문이다. 파일 이름은 문자열이
아니다. 특정 운영 체제에서는 그럴 수도 있겠지만 모두에서 꼭
그런 건 아니다. 바람직한 작성 방식에 대해선 이어지는 절들을 보라.

.. admonition:: 빈 가변 인자에 대해

   ``argparse``\를 써 왔다면 ``nargs``\를 ``+``\로 설정해서 적어도
   한 개 인자는 필요하다는 걸 나타내는 방식이 그리울 수도 있겠다.

   ``required=True``\를 설정해 주면 된다. 하지만 가능하면 쓰지
   않는 게 좋은데, 가변 인자가 비어 있을 때 스크립트가 아무것도
   하지 않고 매끄럽게 끝나는 게 좋을 것 같아서다. 왜냐면 스크립트를
   호출할 때 명령행에서 와일드카드를 입력으로 주는 경우가 빈번한데
   와일드카드가 비어 있을 때도 오류가 나지 않는 게 좋기 때문이다.

.. _file-args:

파일 인자
---------

앞선 모든 예시에 파일명이 있었으니 파일을 제대로 다루는 방법을
설명하는 게 좋을 것 같다. 명령행 도구에서 파일을 다룰 때
유닉스 방식을 쓰면, 즉 stdin/stdout을 나타내는 특수 파일
``-``\를 받으면 더 재밌게 사용할 수 있다.

클릭에서는 파일을 똑똑하게 다뤄 주는 :class:`click.File` 타입을
통해 그런 동작을 지원한다. 이 타입은 또 모든 파이썬 버전에서
유니코드와 bytes를 알맞게 처리해 주며, 그래서 스크립트 이식성이
좋아진다.

예:

.. click:example::

    @click.command()
    @click.argument('input', type=click.File('rb'))
    @click.argument('output', type=click.File('wb'))
    def inout(input, output):
        while True:
            chunk = input.read(1024)
            if not chunk:
                break
            output.write(chunk)

그러면 다음처럼 된다.

.. click:run::

    with isolated_filesystem():
        invoke(inout, args=['-', 'hello.txt'], input=['hello'],
               terminate_input=True)
        invoke(inout, args=['hello.txt', '-'])

파일 경로 인자
--------------

앞선 예에서는 파일들이 즉시 열린다. 하지만 단순히 파일명만 필요한
경우라면 어떨까? 간단하게는 기본인 문자열 인자 타입을 쓸 수 있다.
하지만 클릭은 유니코드 기반이므로 문자열이 항상 유니코드 값이 된다.
그런데 파일명은 사용 운영 체제에 따라 유니코드일 수도 있고 bytes일
수도 있다. 따라서 문자열 타입으로는 충분치 않다.

대신 이런 사항들을 자동으로 처리해 주는 :class:`Path` 타입을 쓰면
된다. 상황에 맞게 bytes와 유니코드 중 한쪽을 반환해 줄 뿐만 아니라
파일 존재 여부 확인 같은 기본적인 검사 몇 가지를 수행할 수도 있다.

예:

.. click:example::

    @click.command()
    @click.argument('f', type=click.Path(exists=True))
    def touch(f):
        click.echo(click.format_filename(f))

그러면 다음처럼 된다.

.. click:run::

    with isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hello World!\n')
        invoke(touch, args=['hello.txt'])
        println()
        invoke(touch, args=['missing.txt'])


파일 열기의 안전성
------------------

:class:`File` 타입에는 고민이 필요한 문제가 하나 있는데, 바로
언제 파일을 열 것인가이다. 기본 동작은 "똑똑하게" 처리하는 것이다.
즉 stdin/stdout이나 읽기용으로 여는 파일은 즉시 연다. 이렇게 하면
파일을 열 수 없을 때 사용자에게 바로 피드백을 주게 된다. 단 쓰기용
파일은 IO 동작을 처음 수행할 때 열게 되며, 그렇게 하기 위해
자동으로 별도의 래퍼로 파일을 감싼다.

생성자에 ``lazy=True``\나 ``lazy=False``\를 줘서 동작 방식을
강제할 수 있다. 파일을 늦게 여는 경우에는 실패 시 첫 IO 동작에서
:exc:`FileError`\를 던지게 된다.

쓰기용으로 파일을 열면 보통 즉시 파일을 비워 버리게 된다. 따라서
원하는 동작 방식이 아니라는 확신이 있는 경우에만 늦게 여는 동작을
비활성화해야 할 것이다.

늦게 여는 방식이 자원 처리에서의 혼란을 피하는 데 크게 도움이 될
수도 있다.  늦게 여는 방식으로 파일을 열면 ``close_intelligently``
메소드를 받는데, 이 메소드는 파일을 닫아야 하는지 여부를 판단하는
걸 돕는다. 매개변수에서는 필요치 않고 :func:`prompt` 함수로
직접 값을 물어볼 때 필요한데, 그때는 (이미 열려 있던) stdout 같은
스트림을 연 것인지 닫아 줘야 할 실제 파일을 연 것인지 알 수 없기
때문이다.

클릭 2.0부터는 ``atomic=True``\를 줘서 파일을 원자 모드로 열
수도 있다. 원자 모드에서는 모든 쓰기 내용이 같은 폴더 내의 별도
파일로 가며 작업이 끝나면 그 파일이 원래 위치로 옮겨지게 된다.
다른 사용자들이 규칙적으로 읽는 파일을 변경하는 경우에 유용하다.

환경 변수
---------

옵션과 마찬가지로 인자도 환경 변수에서 값을 얻어 올 수 있다. 하지만
옵션에서와 달리 명시적으로 환경 변수 이름을 지정해 줘야 한다.

사용례:

.. click:example::

    @click.command()
    @click.argument('src', envvar='SRC', type=click.File('r'))
    def echo(src):
        click.echo(src.read())

명령행:

.. click:run::

    with isolated_filesystem():
        with open('hello.txt', 'w') as f:
            f.write('Hello World!')
        invoke(echo, env={'SRC': 'hello.txt'})

이 경우 여러 환경 변수들의 목록을 쓸 수도 있으며 그러면
첫 번째로 있는 값을 가져온다.

사용자에게 많은 혼란을 줄 수 있으므로 이 기능은 일반적으로
사용을 권하지 않는다.

옵션 같은 인자
--------------

옵션처럼 생긴 인자를 처리하고 싶을 때가 있다. 예를 들어 파일
이름이 ``-foo.txt``\인 경우를 생각해 볼 수 있다. 이런 이름을
인자로 주면 클릭에서는 옵션으로 처리하게 된다.

이를 해결하기 위해 클릭은 여느 POSIX 방식 명령행 스크립트와
같은 방법을 쓰는데, 옵션과 인자를 구분하는 문자열 ``--``\를
받는 것이다. ``--`` 표시 다음에 있는 매개변수는 모두 인자로
받는다.

사용례:

.. click:example::

    @click.command()
    @click.argument('files', nargs=-1, type=click.Path())
    def touch(files):
        for filename in files:
            click.echo(filename)

명령행:

.. click:run::

    invoke(touch, ['--', '-foo.txt', 'bar.txt'])

``--`` 표시 방식이 싫다면 ignore_unknown_options를 True로
설정해서 모르는 옵션을 검사하는 걸 피할 수 있다.

.. click:example::

    @click.command(context_settings={"ignore_unknown_options": True})
    @click.argument('files', nargs=-1, type=click.Path())
    def touch(files):
        for filename in files:
            click.echo(filename)

명령행:

.. click:run::

    invoke(touch, ['-foo.txt', 'bar.txt'])

