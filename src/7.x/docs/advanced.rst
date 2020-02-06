고급 패턴
=========

.. currentmodule:: click

라이브러리에 구현돼 있는 일반적인 기능들에 더해서 클릭을
확장해 구현할 수 있는 패턴들이 많이 있다. 어떤 것들이 가능한지
이 페이지에서 살펴보자.

.. _aliases:

명령 별칭
---------

여러 도구들에서 명령 별칭을 지원한다. 예를 들어 ``git commit``\의
별칭으로 ``git ci``\를 받도록 ``git``\을 설정할 수 있다. 다른
도구들에서는 자동으로 명령을 줄여서 별칭을 자동으로 찾아내는
것도 지원한다.

클릭에선 그 기능을 바로는 지원하지 않는다. 하지만 :class:`Group`\이나
다른 :class:`MultiCommand`\를 변경하면 아주 쉽게 기능을 제공할 수
있다.

:ref:`custom-multi-commands` 절에서 설명한 것처럼 다중 명령에
:meth:`~MultiCommand.list_commands`\와
:meth:`~MultiCommand.get_command`\라는 두 가지 메소드를 제공할
수 있다. 일반적으로 도움말 페이지에 별칭들을 나열해서 복잡하게
만드는 건 피하고 싶을 것이므로 후자만 오버라이드 하면 된다.

다음 예는 명령 앞 부분을 받아들이는 :class:`Group`\의 하위 클래스를
구현한 것이다. 가령 ``push``\라는 명령이 있다면 ``pus``\를
(대응하는 명령이 유일하다면) 별칭으로 받아들이게 된다.

.. click:example::

    class AliasedGroup(click.Group):

        def get_command(self, ctx, cmd_name):
            rv = click.Group.get_command(self, ctx, cmd_name)
            if rv is not None:
                return rv
            matches = [x for x in self.list_commands(ctx)
                       if x.startswith(cmd_name)]
            if not matches:
                return None
            elif len(matches) == 1:
                return click.Group.get_command(self, ctx, matches[0])
            ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))

그러면 다음처럼 사용할 수 있다.

.. click:example::

    @click.command(cls=AliasedGroup)
    def cli():
        pass

    @cli.command()
    def push():
        pass

    @cli.command()
    def pop():
        pass

매개변수 조작
-------------

앞서 본 것처럼 매개변수(옵션과 인자)들이 명령 콜백으로 전달된다.
콜백으로 매개변수가 전달되는 걸 막을 수 있는 방법 하나는
매개변수에 `expose_value` 인자를 줘서 그 매개변수를 완전히
감추는 것이다. 이게 동작하는 방식은 :class:`Context` 객체에
있는 :attr:`~Context.params` 속성을 이용하는 것이다. 이 속성은
모든 매개변수들의 딕셔너리고 그 딕셔너리에 있는 게 모두
콜백으로 전달된다.

그 속성을 이용하면 매개변수를 추가로 만들어 낼 수도 있다.
보통은 권장하지 않는 패턴이지만 어떤 경우에는 유용할 수 있다.
그게 아니더라도 시스템이 이렇게 동작한다는 알아 두는 건 좋은 일이다.

.. click:example::

    import urllib

    def open_url(ctx, param, value):
        if value is not None:
            ctx.params['fp'] = urllib.urlopen(value)
            return value

    @click.command()
    @click.option('--url', callback=open_url)
    def cli(url, fp=None):
        if fp is not None:
            click.echo('%s: %s' % (url, fp.code))

여기서 옵션 콜백은 URL을 변경 없이 반환하면서 명령 콜백에
두 번째 인자 ``fp``\를 준다. 하지만 더 바람직한 방식은
그 정보를 잘 포장해서 전달하는 것이다.

.. click:example::

    import urllib

    class URL(object):

        def __init__(self, url, fp):
            self.url = url
            self.fp = fp

    def open_url(ctx, param, value):
        if value is not None:
            return URL(value, urllib.urlopen(value))

    @click.command()
    @click.option('--url', callback=open_url)
    def cli(url):
        if url is not None:
            click.echo('%s: %s' % (url.url, url.fp.code))


토큰 정규화
-----------

.. versionadded:: 2.0

클릭 2.0부터는 토큰 정규화에 쓸 함수를 주는 게 가능하다. 토큰에
해당하는 건 옵션 이름, 선택지 값, 명령 값이다. 이를 이용하면
예를 들어 대소문자 구별 없는 옵션을 구현할 수 있다.

이 기능을 사용하기 위해선 토큰 정규화를 수행하는 함수를 문맥에
줘야 한다. 예를 들어 다음처럼 토큰을 소문자로 바꾸는 함수를
줄 수 있다.

.. click:example::

    CONTEXT_SETTINGS = dict(token_normalize_func=lambda x: x.lower())

    @click.command(context_settings=CONTEXT_SETTINGS)
    @click.option('--name', default='Pete')
    def cli(name):
        click.echo('Name: %s' % name)

그러면 명령행에서 다음처럼 동작한다.

.. click:run::

    invoke(cli, prog_name='cli', args=['--NAME=Pete'])

다른 명령 호출하기
------------------

때로는 한 명령에서 다른 명령을 호출하고 싶을 수도 있을 것이다.
일반적으로 클릭에서 권장하지 않는 패턴이지만 어쨌든 가능은
하다. :func:`Context.invoke`\나 :func:`Context.forward` 메소드를
이용할 수 있다.

두 메소드는 비슷하게 동작한다. 차이는 :func:`Context.invoke`\는
호출하는 쪽에서 준 인자들로만 다른 명령을 호출하는 반면
:func:`Context.forward`\는 현재 명령의 인자들을 가져다 채우기도
한다는 점이다. 둘 모두 첫 번째 인자로 명령을 받으며 그 외 모든
인자들은 그대로 전달된다.

예:

.. click:example::

    cli = click.Group()

    @cli.command()
    @click.option('--count', default=0)
    def test(count):
        click.echo('Count: %d' % count)

    @cli.command()
    @click.option('--count', default=1)
    @click.pass_context
    def dist(ctx, count):
        ctx.forward(test)
        ctx.invoke(test, count=42)

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='cli', args=['dist'])


.. _callback-evaluation-order:

콜백 평가 순서
--------------

클릭의 동작 방식 중에 몇몇 다른 명령행 파서들과 좀 다른
점이 있는데, 콜백을 호출하기 전에 프로그래머가 규정한 인자
순서와 사용자가 지정한 인자 순서를 조화시키려고 시도한다는
점이다.

optparse 등의 시스템에서 클릭으로 복잡한 패턴들을 이식할 때
이 개념을 잘 이해하고 있어야 한다. optparse에서는 파싱 단계를
진행하면서 매개변수 콜백 호출이 일어나는 반면 클릭에서는 파싱
후에 콜백 호출이 일어난다.

주된 차이는 optparse에서는 있는 그대로의 값으로 콜백을
호출하는 반면 클릭에서는 값을 완전히 변환한 후에 콜백을
호출한다는 점이다.

일반적으로 호출 순서는 사용자가 스크립트에 인자를 제공한
순서에 따라 정해진다. ``--foo``\라는 옵션과 ``--bar``\라는
옵션이 있는데 사용자가 ``--bar --foo``\라고 호출하면
``bar``\의 콜백이 호출된 다음 ``foo``\의 콜백이 불린다.

그 규칙의 세 가지 예외를 알아 둘 필요가 있다.

긴급 표시:
    옵션을 "긴급"으로 설정할 수 있다. 긴급 매개변수들은
    모두 비긴급 매개변수보다 먼저 평가한다. 그리고 그 안에선
    마찬가지로 사용자가 명령행에 준 순서대로 평가한다.

    ``--help``\나 ``--version``\처럼 실행 후 종료하는
    매개변수에서 중요하다. 둘 모두 긴급 매개변수인데,
    명령행에서 먼저인 쪽이 실행 기회를 잡고 프로그램을 끝내게 된다.

반복되는 매개변수:
    옵션이나 인자가 명령행 여러 곳에 나뉘어 있는
    경우에는 (예를 들어 ``--exclude foo --include baz
    --exclude bar``) 첫 번째 옵션 위치에 따라 콜백이 실행된다.
    예로 든 경우에선 ``exclude``\에 대해 콜백이 실행되면서
    두 옵션(``foo`` 및 ``bar``)을 모두 받게 되고, 그 다음에
    ``include``\에 대해 콜백이 실행되면서 ``baz``\만 받게 된다.

    참고로 매개변수에서 여러 값을 허용하지 않는 경우라도 클릭에서는
    위치는 첫 번째 걸로 받고 값은 마지막 값을 빼고 모두 무시하게
    된다. 이렇게 하는 이유는 기본값을 설정하는 셸 알리아스를
    통해서도 조합해서 사용이 가능하게 하기 위해서다.

빠진 매개변수:
    명령행에서 매개변수를 지정하지 않은 경우에도 콜백이
    실행된다. 반면 optparse에서는 값을 지정하지 않으면
    콜백이 실행되지 않는다. 빠진 매개변수들의 콜백은 가장
    마지막에 실행되며, 따라서 앞에 온 매개변수들에서 얻은
    값들로 기본값을 정하는 것도 가능하다.

대부분의 경우는 이 중 어느 것에도 신경쓸 필요가 없지만 일부
복잡한 경우를 생각해서 동작 방식은 알아두는 게 좋다.

.. _forwarding-unknown-options:

모르는 옵션 전달
----------------

모르는 옵션들을 모두 받아서 추가로 수동 처리를 할 수 있으면
하는 경우들이 좀 있다. 클릭 4.0 기준으로 일반적으로 클릭에서
그렇게 하는 게 가능하지만 문제의 특성에서 비롯한 한계가
좀 있다. ``ignore_unknown_options``\라는 파서 플래그를 통해
이를 지원하는데, 그 플래그는 파서에서 모르는 옵션이 있으면
파싱 오류를 일으키는 대신 모두 모아 뒀다가 나머지
인자로 넘기게 한다.

일반적으로 두 가지 방식으로 이를 활성화할 수 있다.

1.  새로운 :class:`Command` 하위 클래스에서
    :attr:`~BaseCommand.ignore_unknown_options` 속성을 켤 수 있다.
2.  문맥 클래스의 같은 이름
    속성(:attr:`Context.ignore_unknown_options`)을 바꿔서 켤 수 있다.
    명령의 ``context_settings`` 딕셔너리를 통해 바꾸는 게 가장 편하다.

대부분의 경우에 쉬운 방법은 두 번째다. 그렇게 동작 방식을
바꾸고 나면 어디선가 그 나머지 옵션들을 (이 시점에선 인자로
본다) 가져가야 한다. 여기에도 두 가지 방법이 있다.

1.  :func:`pass_context`\를 써서 문맥이 전달되게 할 수 있다.
    이게 동작하려면 :attr:`~Context.ignore_unknown_options`\에
    더해 :attr:`~Context.allow_extra_args`\도 설정해 줘야 한다.
    안 그러면 나머지 인자가 있다는 오류와 함께 명령 처리가
    중단된다. 이 방식으로 가는 경우 추가 인자들은
    :attr:`Context.args`\에 모여 있게 된다.
2.  :func:`argument`\를 ``nargs``\를 `-1`\로 해서 붙이면
    나머지 인자들을 모두 잡아먹게 된다. 이 경우 `type`\을
    :data:`UNPROCESSED`\로 설정해서 그 인자들에 문자열 처리가
    이뤄지는 걸 막는 게 좋다. 안 그러면 자동으로 유니코드
    문자열로 바뀌는데, 원하는 동작이 아닌 경우가 많다.

종합하면 다음과 비슷하게 된다.

.. click:example::

    import sys
    from subprocess import call

    @click.command(context_settings=dict(
        ignore_unknown_options=True,
    ))
    @click.option('-v', '--verbose', is_flag=True, help='상세 출력 모드 켜기')
    @click.argument('timeit_args', nargs=-1, type=click.UNPROCESSED)
    def cli(verbose, timeit_args):
        """파이썬 timeit 래퍼인 척하기."""
        cmdline = ['echo', 'python', '-mtimeit'] + list(timeit_args)
        if verbose:
            click.echo('Invoking: %s' % ' '.join(cmdline))
        call(cmdline)

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='cli', args=['--help'])
    println()
    invoke(cli, prog_name='cli', args=['-n', '100', 'a = 1; b = 2; a * b'])
    println()
    invoke(cli, prog_name='cli', args=['-v', 'a = 1; b = 2; a * b'])

보다시피 상세 출력 플래그는 클릭에서 처리하고 나머지는 모두
`timeit_args` 변수로 들어가며, 그래서 이후 처리에서 가령 하위
프로세스를 실행하거나 할 수 있다. 이 비처리 플래그 무시 플래그의
동작 방식에 대해 알아 둬야 할 게 몇 가지 있다.

*   모르는 긴 옵션은 일반적으로 무시돼서 전혀 처리되지 않는다.
    그래서 예를 들어 ``--foo=bar`` 내지 ``--foo bar``\라고 주면
    일반적으로 그런 식으로 된다. 참고로 파서에서는 옵션이 인자를
    받는지 여부를 알 수 없기 때문에 ``bar`` 부분이 명령 인자로
    처리될 수도 있다.
*   모르는 짧은 옵션들이 필요시 일부만 처리되고 재조합될 수도 있다.
    예를 들어 위 예시에는 상세 출력 모드를 켜는 ``-v``\라는 옵션이
    있다. 명령에 ``-va``\를 준다면 ``-v`` 부분은 (아는 옵션이므로)
    클릭에서 처리하고 ``-a``\가 남아서 나머지 매개변수로 마저
    처리될 것이다.
*   뭘 하려느냐에 따라선 인자 섞어 쓰기를 꺼서
    (:attr:`~Context.allow_interspersed_args`) 원하는 결과를 얻을
    수도 있다. 그 동작을 끄면 인자와 옵션이 섞여 있는 걸 파서에서
    허용하지 않게 된다. 상황에 따라 더 나은 결과를 얻을 수도 있다.

일반적으로 자체 명령과 다른 응용에서 온 명령의 옵션과
인자를 합쳐서 처리하는 건 바람직하지 않으며 가능하면 피하는 게
좋다. 일부 인자들을 직접 처리하는 것보단 하위 명령 아래 있는
모든 항목을 다른 응용으로 전달해 주는 게 훨씬 낫다.


전역 문맥 접근
--------------

.. versionadded:: 5.0

클릭 5.0부터는 동일 스레드 내의 어디서도 현재 문맥에 접근하는 게
가능하다. :func:`get_current_context` 함수를 쓰면 현재
문맥을 반환해 준다. 문맥에 연결된 객체나 거기 저장된 플래그에
접근해서 런타임 동작을 적절히 바꾸는 데 주로 쓸모가 있다.
예를 들어 :func:`echo` 함수에서 이를 통해 `color` 플래그의
기본값을 알아낸다.

사용례::

    def get_current_command_name():
        return click.get_current_context().info_name

현재 스레드 내에서만 동작한다는 점에 유의하자. 스레드를 추가로
만들면 그 스레드에서는 현재 문맥을 참조할 수 없게 된다.
다른 스레드에서 현재 문맥을 참조할 수 있게 하고 싶다면
문맥 관리자로서 그 스레드 내에서 문맥을 써야 한다. ::

    def spawn_thread(ctx, func):
        def wrapper():
            with ctx:
                func()
        t = threading.Thread(target=wrapper)
        t.start()
        return t

그러면 스레드 함수에서 메인 스레드처럼 문맥에 접근할 수 있게
된다. 하지만 스레드 사용을 위해 이렇게 할 때는 아주 조심할
필요가 있는데, 문맥 대부분은 스레드에 안전하지 않기 때문이다.
즉 문맥에서 읽는 것만 가능하고 변경을 수행하는 건 안 된다.
