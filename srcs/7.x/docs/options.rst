.. _options:

옵션
====

.. currentmodule:: click

:func:`option` 데코레이터를 이용해 명령에 옵션을 추가할 수 있다.
옵션들의 형태는 다양하므로 동작 방식을 설정하기 위한 매개변수들이
많이 있다. 클릭에서는 옵션과 :ref:`위치 인자 <arguments>`\를
구별한다.

옵션 이름
---------

:ref:`parameter_names` 절에서 명명 규칙을 볼 수 있다. 요약하면
앞에 대시가 붙은 가장 긴 인자로 옵션을 **묵시적으로** 가리킬 수 있다.

.. click:example::

    @click.command()
    @click.option('-s', '--string-to-echo')
    def echo(string_to_echo):
        click.echo(string_to_echo)

또는 대시 없는 인자를 줘서 **명시적으로** 가리킬 수도 있다.

.. click:example::

    @click.command()
    @click.option('-s', '--string-to-echo', 'string')
    def echo(string):
        click.echo(string)

기본 값 옵션
------------

가장 기본적인 옵션은 값 옵션이다. 이 옵션들은 값 인자 하나를 받는다.
타입을 주지 않으면 기본값의 타입을 쓴다. 기본값을 주지 않으면 타입이
:data:`STRING`\이라고 상정한다. 이름을 명시적으로 지정하지 않으면
정의된 첫 번째 긴 옵션이 매개변수 이름이 된다. 없으면 첫 번째 짧은
옵션을 쓴다. 기본적으로 옵션은 필수가 아니다. 옵션을 필수로 만들려면
데코레이터 인자로 `required=True`\를 주면 된다.

.. click:example::

    @click.command()
    @click.option('--n', default=1)
    def dots(n):
        click.echo('.' * n)

.. click:example::

    # 옵션을 필수로 만들기
    @click.command()
    @click.option('--n', required=True, type=int)
    def dots(n):
        click.echo('.' * n)

.. click:example::

    # 매개변수로 `from` 같은 파이썬 예약어 쓰기
    @click.command()
    @click.option('--from', '-f', 'from_')
    @click.option('--to', '-t')
    def reserved_param_name(from_, to):
        click.echo('from %s to %s' % (from_, to))

명령행:

.. click:run::

   invoke(dots, args=['--n=2'])

이 경우 기본값이 정수이므로 옵션이 :data:`INT` 타입이다.

명령 도움말을 보일 때 기본값을 표시하려면 ``show_default=True``\를
쓰면 된다.

.. click:example::

    @click.command()
    @click.option('--n', default=1, show_default=True)
    def dots(n):
        click.echo('.' * n)

.. click:run::

   invoke(dots, args=['--help'])

여러 값 옵션
------------

때로는 인자를 여러 개 받는 옵션이 있다. 옵션에서는 고정 개수 인자만
지원된다. ``nargs`` 매개변수로 개수를 설정할 수 있다. 그러면 값들이
튜플로 저장된다.

.. click:example::

    @click.command()
    @click.option('--pos', nargs=2, type=float)
    def findme(pos):
        click.echo('%s / %s' % pos)

명령행:

.. click:run::

    invoke(findme, args=['--pos', '2.0', '3.0'])

.. _tuple-type:

여러 값 튜플 옵션
-----------------

.. versionadded:: 4.0

보다시피 `nargs`\를 써서 개수를 지정하면 결과 튜플의 각 항목이
같은 타입이 된다. 원하는 게 이게 아닐 수도 있다. 보통은 튜플
인덱스에 따라 다른 타입을 쓰고 싶을 수도 있을 것이다.
그렇다면 타입을 직접 튜플로 지정할 수 있다.

.. click:example::

    @click.command()
    @click.option('--item', type=(str, int))
    def putitem(item):
        click.echo('name=%s id=%d' % item)

명령행:

.. click:run::

    invoke(putitem, args=['--item', 'peter', '1338'])

튜플 리터럴을 타입으로 쓰면 `nargs`\가 자동으로 그 튜플 길이로
설정되고 자동으로 :class:`click.Tuple` 타입이 쓰인다.
즉 위 예는 다음과 동등하다.

.. click:example::

    @click.command()
    @click.option('--item', nargs=2, type=click.Tuple([str, int]))
    def putitem(item):
        click.echo('name=%s id=%d' % item)

다중 옵션
---------

``nargs``\와 비슷하게 매개변수를 여러 번 지정하는 걸 지원하면서
(마지막 값만이 아니라) 모든 값이 기록되게 하고 싶은 경우도 있다.
예를 들어 ``git commit -m foo -m bar``\라고 하면 커밋 메시지를
``foo``\와 ``bar`` 두 줄 기록하게 된다. ``multiple`` 플래그로
그렇게 할 수 있다.

예:

.. click:example::

    @click.command()
    @click.option('--message', '-m', multiple=True)
    def commit(message):
        click.echo('\n'.join(message))

명령행:

.. click:run::

    invoke(commit, args=['-m', 'foo', '-m', 'bar'])

개수 세기
---------

일부 아주 드문 상황에선 옵션 반복 횟수를 정수로 세고 싶을 수 있다.
예를 들어 상세 수준 플래그에 쓸 수 있다.

.. click:example::

    @click.command()
    @click.option('-v', '--verbose', count=True)
    def log(verbose):
        click.echo('Verbosity: %s' % verbose)

명령행:

.. click:run::

    invoke(log, args=['-vvv'])

불리언 플래그
-------------

불리언 플래그란 켜거나 끌 수 있는 옵션이다. 옵션을 켜거나 끄기
위한 두 플래그를 슬래시(``/``)로 구분해서 한꺼번에 정의하면 된다.
(옵션 문자열 안에 슬래시가 있으면 클릭에선 자동으로 불리언
플래그임을 알고 암묵적으로 ``is_flag=True``\를 전달한다.)
클릭에서는 나중에 기본값을 바꿀 수 있도록 항상 켜는 플래그와
끄는 플래그를 모두 제공하기를 기대한다.

예:

.. click:example::

    import sys

    @click.command()
    @click.option('--shout/--no-shout', default=False)
    def info(shout):
        rv = sys.platform
        if shout:
            rv = rv.upper() + '!!!!111'
        click.echo(rv)

명령행:

.. click:run::

    invoke(info, args=['--shout'])
    invoke(info, args=['--no-shout'])

끄는 스위치가 정말 필요 없다면 한쪽만 정의하고 그게 플래그라는
걸 클릭에게 수동으로 알려 주면 된다.

.. click:example::

    import sys

    @click.command()
    @click.option('--shout', is_flag=True)
    def info(shout):
        rv = sys.platform
        if shout:
            rv = rv.upper() + '!!!!111'
        click.echo(rv)

명령행:

.. click:run::

    invoke(info, args=['--shout'])

참고로 옵션에 이미 슬래시가 들어간다면 (예를 들어 ``/``\가 앞에 오는
윈도우 방식 매개변수를 쓴다면) 대신 ``;``\을 써서 매개변수들을
나눌 수 있다.

.. click:example::

    @click.command()
    @click.option('/debug;/no-debug')
    def log(debug):
        click.echo('debug=%s' % debug)

    if __name__ == '__main__':
        log()

.. versionchanged:: 6.0

두 번째 옵션에만 별칭을 주고 싶다면 형식 문자열에서 앞에 공백을
줘서 구별해 줘야 한다.

예:

.. click:example::

    import sys

    @click.command()
    @click.option('--shout/--no-shout', ' /-S', default=False)
    def info(shout):
        rv = sys.platform
        if shout:
            rv = rv.upper() + '!!!!111'
        click.echo(rv)

.. click:run::

    invoke(info, args=['--help'])

기능 스위치
-----------

불리언 플래그 말고도 기능 스위치라는 것도 있다. 같은 매개변수 이름으로
여러 옵션을 설정하고 플래그 값을 정의해 주면 된다. 참고로
``flag_value`` 매개변수를 주면 클릭에서 암묵적으로 ``is_flag=True``\를
설정한다.

기본 플래그를 설정하려면 기본으로 할 플래그에 ``default``\를
`True`\로 할당해 주면 된다.

.. click:example::

    import sys

    @click.command()
    @click.option('--upper', 'transformation', flag_value='upper',
                  default=True)
    @click.option('--lower', 'transformation', flag_value='lower')
    def info(transformation):
        click.echo(getattr(sys.platform, transformation)())

명령행:

.. click:run::

    invoke(info, args=['--upper'])
    invoke(info, args=['--lower'])
    invoke(info)

.. _choice-opts:

선택 옵션
---------

때로는 값 목록에서 고르는 매개변수가 필요하다. 그런 경우
:class:`Choice` 타입을 쓸 수 있다. 유효한 값들의 목록을 줘서
생성할 수 있다.

예:

.. click:example::

    @click.command()
    @click.option('--hash-type', type=click.Choice(['md5', 'sha1']))
    def digest(hash_type):
        click.echo(hash_type)

다음처럼 된다.

.. click:run::

    invoke(digest, args=['--hash-type=md5'])
    println()
    invoke(digest, args=['--hash-type=foo'])
    println()
    invoke(digest, args=['--help'])

.. note::

    선택지를 리스트나 튜플로만 줘야 한다. (제너레이터 같은) 다른
    이터러블은 예상치 못한 결과를 유발할 수 있다.

.. _option-prompting:

값 묻기
-------

어떤 경우에는 명령행에서 줄 수도 있지만 안 주면 사용자 입력을
요구하는 매개변수가 필요하다. 클릭에서는 ``prompt``\를 `True`\로
정의해 주면 된다.

예:

.. click:example::

    @click.command()
    @click.option('--name', prompt=True)
    def hello(name):
        click.echo('Hello %s!' % name)

그러면 다음처럼 된다.

.. click:run::

    invoke(hello, args=['--name=John'])
    invoke(hello, input=['John'])

기본 질문 문자열이 마음에 들지 않는다면 다른 문자열로
물을 수 있다.

.. click:example::

    @click.command()
    @click.option('--name', prompt='Your name please')
    def hello(name):
        click.echo('Hello %s!' % name)

다음처럼 된다.

.. click:run::

    invoke(hello, input=['John'])

패스워드 묻기
-------------

클릭에서는 글자 숨기기와 확인용 재입력도 지원한다. 패스워드 입력에
유용하다.

.. click:example::

    @click.command()
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True)
    def encrypt(password):
        click.echo('Encrypting password to %s' % password.encode('rot13'))

다음처럼 된다.

.. click:run::

    invoke(encrypt, input=['secret', 'secret'])

매개변수들을 이렇게 조합해 쓰는 게 꽤 흔하기 때문에 대신
:func:`password_option` 데코레이터를 쓸 수도 있다.

.. click:example::

    @click.command()
    @click.password_option()
    def encrypt(password):
        click.echo('Encrypting password to %s' % password.encode('rot13'))

동적 프롬프트 기본값
--------------------

문맥 옵션 ``auto_envvar_prefix`` 및 ``default_map``\을 통해
환경이나 설정 파일로부터 옵션 값을 읽을 수 있다.
하지만 이 방식은 프롬프트 동작을 무시하며, 그래서 사용자가
대화식으로 값을 바꿀 방법이 없다.

사용자가 기본값을 설정할 수 있도록 하되 명령행에 옵션이 없으면
물어보도록 하고 싶다면 기본값으로 호출 가능 객체를 주면 된다.
예를 들어 환경에서 기본값을 얻으려면 다음처럼 하면 된다.

.. click:example::

    @click.command()
    @click.option('--username', prompt=True,
                  default=lambda: os.environ.get('USER', ''))
    def hello(username):
        print("Hello,", username)

뭐가 기본값이 되는지 설명해 주려면 ``show_default``\에 설정하면 된다.

.. click:example::

    @click.command()
    @click.option('--username', prompt=True,
                  default=lambda: os.environ.get('USER', ''),
                  show_default='current user')
    def hello(username):
        print("Hello,", username)

.. click:run::

   invoke(hello, args=['--help'])

콜백과 긴급 옵션
----------------

때로는 매개변수에 의해 실행 흐름이 완전히 달라지게 하고 싶은
경우가 있다. 예를 들어 ``--version`` 매개변수가 있어서 버전을
찍고 바로 응용을 끝내고 싶은 경우가 그렇다.

참고: 재사용 가능한 ``--version`` 매개변수 구현이 클릭에
:func:`click.version_option`\으로 포함돼 있다. 여기 있는 코드는
그런 플래그를 어떻게 구현할 수 있는지 보여 주기 위한 예일 뿐이다.

그런 경우에 두 가지 개념이 필요한데, 긴급(eager) 매개변수와
콜백이다. 긴급 매개변수란 다른 것보다 먼저 처리하는 매개변수이고
콜백은 매개변수 처리 후에 실행되는 것이다. 앞쪽의 필수 매개변수
때문에 오류 메시지가 나오는 걸 피하기 위해 긴급도가 필요하다.
예를 들어 ``--version``\이 긴급 매개변수가 아닌데 매개변수
``--foo``\가 필수이고 먼저 정의돼 있으면 그 매개변수를 지정해
줘야 ``--version``\이 동작하게 된다. 자세한 내용은
:ref:`callback-evaluation-order` 참고.

콜백은 함수이며 현재 :class:`Context` 및 값으로 호출된다.
문맥을 통해 응용 끝내기 같은 몇 가지 유용한 동작을 이용하고
이미 처리된 다른 매개변수들에 접근할 수 있다.

다음은 ``--version`` 플래그 예시이다.

.. click:example::

    def print_version(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        click.echo('Version 1.0')
        ctx.exit()

    @click.command()
    @click.option('--version', is_flag=True, callback=print_version,
                  expose_value=False, is_eager=True)
    def hello():
        click.echo('Hello World!')

`expose_value` 매개변수는 별 의미 없는 ``version`` 매개변수가
콜백으로 전달되지 않도록 한다. 지정하지 않으면 `hello` 스크립트로
불리언 하나가 전달된다. `resilient_parsing` 플래그는 실행 흐름을
바꿀 파괴적 동작 없이 명령행 파싱을 수행하기를 클릭에서 원할 때
설정된다. 이 경우 프로그램에서 빠져나가게 될 테니까 설정 시
아무것도 하지 않는다.

다음처럼 된다.

.. click:run::

    invoke(hello)
    invoke(hello, args=['--version'])

.. admonition:: 콜백 시그너처 변경

    클릭 2.0에서 콜백 시그너처가 바뀌었다. 이에 대한
    자세한 내용은 :ref:`upgrade-to-2.0` 참고.

Yes 매개변수
------------

위험한 동작에 대해 사용자 확인을 받을 수 있으면 아주 좋을 것이다.
불리언 플래그 ``--yes``\를 추가하고서 사용자가 그 플래그를 주지
않으면 콜백이 실패하도록 할 수 있다.

.. click:example::

    def abort_if_false(ctx, param, value):
        if not value:
            ctx.abort()

    @click.command()
    @click.option('--yes', is_flag=True, callback=abort_if_false,
                  expose_value=False,
                  prompt='Are you sure you want to drop the db?')
    def dropdb():
        click.echo('Dropped all tables!')

그러면 명령행에서 다음처럼 된다.

.. click:run::

    invoke(dropdb, input=['n'])
    invoke(dropdb, args=['--yes'])

매개변수들을 이렇게 조합해 쓰는 게 꽤 흔하기 때문에 대신
:func:`confirmation_option` 데코레이터를 쓸 수도 있다.

.. click:example::

    @click.command()
    @click.confirmation_option(prompt='Are you sure you want to drop the db?')
    def dropdb():
        click.echo('Dropped all tables!')

.. admonition:: 콜백 시그너처 변경

    클릭 2.0에서 콜백 시그너처가 바뀌었다. 이에 대한
    자세한 내용은 :ref:`upgrade-to-2.0` 참고.

환경 변수에서 값 얻기
---------------------

클릭에서 유용한 기능으로 정규 매개변수뿐 아니라 환경 변수로부터
매개변수를 받는 동작이 있다. 이를 통해 도구들을 손쉽게
자동화할 수 있다. 예를 들어 설정 파일을 ``--config`` 매개변수로
줄 수도 있겠지만 더 편한 개발을 위해 ``TOOL_CONFIG=hello.cfg``
처럼 키-값 쌍으로 지정할 수도 있을 것이다.

클릭에서는 두 가지 방식을 지원한다. 하나는 환경 변수를 자동으로
구성해 주는 방식으로, 옵션에서만 가능하다. 이 기능을 켜려면
스크립트를 호출할 때 ``auto_envvar_prefix`` 매개변수를 줘야 한다.
그러면 각 명령 및 매개변수에 대해 밑줄로 구분된 대문자 변수가
추가된다. 가령 ``foo``\라는 하위 명령이 있어서 ``bar``\라는
옵션을 받으며 접두 문자열이 ``MY_TOOL``\이라면 변수는
``MY_TOOL_FOO_BAR``\가 된다.

사용례:

.. click:example::

    @click.command()
    @click.option('--username')
    def greet(username):
        click.echo('Hello %s!' % username)

    if __name__ == '__main__':
        greet(auto_envvar_prefix='GREETER')

명령행:

.. click:run::

    invoke(greet, env={'GREETER_USERNAME': 'john'},
           auto_envvar_prefix='GREETER')

명령 그룹에 ``auto_envvar_prefix``\를 쓸 때는 환경 변수의
접두 문자열과 매개변수 이름 사이에 명령 이름이 들어가야 한다.
즉 *PREFIX_COMMAND_VARIABLE*\이다.

예:

.. click:example::

   @click.group()
   @click.option('--debug/--no-debug')
   def cli(debug):
       click.echo('Debug mode is %s' % ('on' if debug else 'off'))

   @cli.command()
   @click.option('--username')
   def greet(username):
       click.echo('Hello %s!' % username)

   if __name__ == '__main__':
       cli(auto_envvar_prefix='GREETER')

.. click:run::

   invoke(cli, args=['greet',],
          env={'GREETER_GREET_USERNAME': 'John', 'GREETER_DEBUG': 'false'},
          auto_envvar_prefix='GREETER')


두 번째 방식은 옵션에 환경 변수 이름을 지정해서 직접 특정
환경 변수의 값을 가져오는 방식이다.

사용례:

.. click:example::

    @click.command()
    @click.option('--username', envvar='USERNAME')
    def greet(username):
        click.echo('Hello %s!' % username)

    if __name__ == '__main__':
        greet()

명령행:

.. click:run::

    invoke(greet, env={'USERNAME': 'john'})

이 경우 여러 환경 변수들의 목록을 쓸 수도 있으며 그러면
첫 번째로 있는 값을 가져온다.

환경 값에서 여러 값 얻기
------------------------

옵션에서 여러 값을 받을 수 있을 때 (문자열인) 환경 변수에서
여러 값을 가져오는 건 좀 더 복잡하다. 클릭에서는 각 타입에서
적당한 방식으로 동작하게 맡기는 방식으로 이 문제를 해결한다.
``multiple``\이나 ``1`` 아닌 ``nargs``\가 있을 때 클릭에서
:meth:`ParamType.split_envvar_value` 메소드를 호출해서
분리를 수행하게 된다.

모든 타입에서 기본 구현은 공백에서 나누는 것이다. 단 예외로
:class:`File` 및 :class:`Path` 타입은 운영 체제의 경로 분리
규칙에 따라 나눈다. 리눅스나 OS X 같은 유닉스 시스템에서는
콜론(``:``)에서 분리가 일어나고 윈도우에서는
세미콜론(``;``)에서 일어난다.

사용례:

.. click:example::

    @click.command()
    @click.option('paths', '--path', envvar='PATHS', multiple=True,
                  type=click.Path())
    def perform(paths):
        for path in paths:
            click.echo(path)

    if __name__ == '__main__':
        perform()

명령행:

.. click:run::

    import os
    invoke(perform, env={'PATHS': './foo/bar%s./test' % os.path.pathsep})

다른 시작 문자
--------------

클릭에서는 앞에 ``-`` 대신 다른 문자를 쓰는 옵션을 다룰 수 있다.
예를 들어 슬래시를 매개변수 ``/``\로나 그 비슷하게 처리하고 싶을
때 유용하다. 참고로 일반적으로 가능하면 그렇게 하지 않는 게 좋다.
클릭에서는 개발자들이 POSIX 동작 방식과 비슷하게 하길 바라기
때문이다. 하지만 어떤 경우에는 이게 유용할 수도 있다.

.. click:example::

    @click.command()
    @click.option('+w/-w')
    def chmod(w):
        click.echo('writable=%s' % w)

    if __name__ == '__main__':
        chmod()

명령행:

.. click:run::

    invoke(chmod, args=['+w'])
    invoke(chmod, args=['-w'])

참고로 접두 문자로 ``/``\를 쓰고 있을 때 불리언 플래그를 사용하고
싶으면 ``/`` 대신 ``;``\로 분리해 줘야 한다.

.. click:example::

    @click.command()
    @click.option('/debug;/no-debug')
    def log(debug):
        click.echo('debug=%s' % debug)

    if __name__ == '__main__':
        log()

.. _ranges:

범위 옵션
---------

:class:`IntRange` 타입은 따로 언급할 필요가 있다. 이 타입은
:data:`INT` 타입과 아주 비슷하게 동작하되 그 값을 (양쪽 경계를
포함하는) 특정 범위로 제약한다. 두 가지 동작 모드가 있다.

-   기본 모드(안 자르기 모드)에서는 값이 범위를 벗어나면 오류를
    일으킨다.
-   선택적인 자르기 모드에서는 값이 범위를 벗어나면 잘리게
    된다. 즉 (예를 들어) 범위가 ``0-5``\일 때 ``10`` 값은
    ``5``\를 반환하고 ``-1`` 값은 ``0``\을 반환하게 된다.

예:

.. click:example::

    @click.command()
    @click.option('--count', type=click.IntRange(0, 20, clamp=True))
    @click.option('--digit', type=click.IntRange(0, 10))
    def repeat(count, digit):
        click.echo(str(digit) * count)

    if __name__ == '__main__':
        repeat()

명령행:

.. click:run::

    invoke(repeat, args=['--count=1000', '--digit=5'])
    invoke(repeat, args=['--count=1000', '--digit=12'])

경계 중 어느 쪽에든 ``None``\을 주면 범위 그쪽이 열려 있다는
뜻이다.

검증 콜백
---------

.. versionchanged:: 2.0

별도의 검증 로직을 적용하고 싶다면 매개변수 콜백에서 하면 된다.
그 콜백은 검증이 실패했을 때 오류를 던질 수 있을 뿐 아니라
값을 변경할 수도 있다.

클릭 1.0에서는 :exc:`UsageError`\만 던질 수 있지만 클릭 2.0부터는
:exc:`BadParameter`\도 던질 수 있는데, 자동으로 매개변수 이름을
포함한 오류 메시지를 만들어 준다는 장점이 있다.

예:

.. click:example::

    def validate_rolls(ctx, param, value):
        try:
            rolls, dice = map(int, value.split('d', 2))
            return (dice, rolls)
        except ValueError:
            raise click.BadParameter('rolls need to be in format NdM')

    @click.command()
    @click.option('--rolls', callback=validate_rolls, default='1d6')
    def roll(rolls):
        click.echo('Rolling a %d-sided dice %d time(s)' % rolls)

    if __name__ == '__main__':
        roll()

그러면 다음처럼 된다.

.. click:run::

    invoke(roll, args=['--rolls=42'])
    println()
    invoke(roll, args=['--rolls=2d12'])
