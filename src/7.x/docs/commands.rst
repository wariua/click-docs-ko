명령과 그룹
===========

.. currentmodule:: click

클릭의 가장 중요한 기능은 명령행 도구들로 마음대로 계층 구조를
만들 수 있다는 것이다. :class:`Command`\와 :class:`Group`
(:class:`MultiCommand`)를 통해 구현한다.

콜백 호출
---------

일반 명령에서는 명령이 실행될 때마다 콜백이 실행된다. 스크립트에
명령이 유일하면 매번 호출된다. (매개변수 콜백에서 막는 경우는
예외다. 예를 들어 스크립트에 ``--help``\를 주는 경우가 그렇다.)

그룹 및 다중 명령에서는 상황이 달라진다. 그 경우에는 (동작 방식을
바꾸지 않았다면) 하위 명령이 불릴 때마다 콜백이 불린다. 이게
무슨 뜻이냐면 내부 명령이 실행될 때 외부 명령도 실행된다는 것이다.

.. click:example::

    @click.group()
    @click.option('--debug/--no-debug', default=False)
    def cli(debug):
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))

    @cli.command()
    def sync():
        click.echo('Syncing')

다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='tool.py')
    println()
    invoke(cli, prog_name='tool.py', args=['--debug', 'sync'])

매개변수 전달
-------------

클릭에서는 명령과 하위 명령 간에 매개변수를 엄격하게 구분한다.
이게 무슨 뜻이냐면 어떤 명령에 대한 옵션과 인자는 그 명령 이름
*뒤에*, 그리고 다음 명령이 있다면 그 명령 이름 *앞에* 지정해야
한다는 것이다.

이미 정의돼 있는 ``--help`` 옵션에서도 이 동작을 볼 수 있다.
가령 ``tool.py``\라는 프로그램이 있고 거기에 ``sub``\라는
하위 명령이 있다고 하자.

- ``tool.py --help``\라고 하면 프로그램 전체의 (하위 명령들을
  나열하는) 도움말이 나온다.

- ``tool.py sub --help``\라고 하면 하위 명령 ``sub``\의 도움말이
  나온다.

- 하지만 ``tool.py --help sub``\라고 하면 ``--help``\를 주
  프로그램의 인자로 취급한다. 그럼 클릭에서 ``--help``\의 콜백을
  호출하고, 그러면 도움말을 찍고서 프로그램 실행을 중단한다.
  그래서 하위 명령은 처리하지 못한다.

계층 처리와 문맥
-----------------

앞선 예에서 볼 수 있듯 기본 명령 그룹은 콜백으로 전달되는 debug
인자를 받지만 sync 명령은 받지 못한다. sync 명령은 자체 인자만
받는다.

덕분에 도구들이 서로 완전히 독립적으로 동작할 수 있다. 하지만
어떤 명령에서 하위 명령으로 뭔가를 전달하려면 어떡해야 할까?
답은 :class:`Context`\다.

명령이 호출될 때마다 새 문맥이 생성돼서 부모 문맥에 연결된다.
보통은 그 문맥들을 볼 수 없지만 분명 그렇게 존재한다.
문맥은 매개변수 콜백에 자동으로 값과 함께 전달된다.
그리고 명령에서도 :func:`pass_context` 데코레이터로 표시를
해서 문맥을 전달받을 수 있다. 그 경우 문맥이 첫 번째 인자로
전달된다.

프로그램 자체 용도를 위해 프로그램에서 지정한 객체를 문맥이
가지고 있을 수 있다. 즉 다음처럼 스크립트를 만들 수 있다.

.. click:example::

    @click.group()
    @click.option('--debug/--no-debug', default=False)
    @click.pass_context
    def cli(ctx, debug):
        # ctx.obj가 존재하는지, 그리고 dict인지 (아래의 `if` 블록
        # 아닌 경로로 `cli()`가 호출되는 경우 대비) 확인한다
        ctx.ensure_object(dict)

        ctx.obj['DEBUG'] = debug

    @cli.command()
    @click.pass_context
    def sync(ctx):
        click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))

    if __name__ == '__main__':
        cli(obj={})

객체가 제공되면 각 문맥에서 그 객체를 자식들로 계속 전달한다.
단 어느 단계에서든 문맥의 객체를 바꿀 수 있다. 부모 문맥에
접근하려면 ``context.parent``\를 이용하면 된다.

추가로, 객체를 내려 주는 방식 대신 응용에서 전역 상태를 변경하는
것도 얼마든 가능하다. 예를 들어 그냥 전역의 ``DEBUG`` 변수를
바꾸는 식으로 할 수도 있다.

명령 데코레이터
---------------

앞선 예에서 본 것처럼 데코레이터를 써서 명령이 호출되는 방식을
바꿀 수 있다. 배후에서 실제 일어나는 동작은 콜백은 항상
:meth:`Context.invoke` 메소드를 통해 호출되고 그 메소드에서
자동으로 명령을 올바르게 (문맥을 전달하며, 또는 하지 않으며)
호출하는 것이다.

이게 유용한 건 새로운 데코레이터를 작성하고 싶을 때다. 예를 들어
흔한 패턴으로 상태를 나타내는 객체를 구성해서 문맥에 저장해 둔
다음 새로운 데코레이터를 사용해 그런 최근 객체를 첫 번째 인자로
전달해 주는 방식이 있다.

예를 들어 :func:`pass_obj` 데코레이터를 다음처럼 구현할 수 있다.

.. click:example::

    from functools import update_wrapper

    def pass_obj(f):
        @click.pass_context
        def new_func(ctx, *args, **kwargs):
            return ctx.invoke(f, ctx.obj, *args, **kwargs)
        return update_wrapper(new_func, f)

:meth:`Context.invoke`\에서 함수를 올바른 방식으로 호출해 준다.
즉 :func:`pass_context`\로 꾸며 줬는지 여부에 따라 함수가
``f(ctx, obj)``\나 ``f(obj)`` 중 하나로 호출된다.

이 강력한 개념을 이용하면 아주 복잡한 중첩 응용을 만들 수 있다.
자세한 내용은 :ref:`complex-guide` 참고.


명령 없이 그룹 호출하기
-----------------------

기본적으로 그룹 내지 다중 명령은 하위 명령을 주지 않는 한 호출되지
않는다. 실제로 명령을 주지 않으면 기본적으로 ``--help``\가 자동으로
들어간다. 이 동작 방식을 바꾸려면 그룹에
``invoke_without_command=True``\를 주면 된다. 그러면 도움말
페이지를 보이는 대신 항상 콜백을 호출한다. 그리고 문맥 객체에는
호출이 하위 명령으로 가게 되는지 여부에 대한 정보가 있다.

예:

.. click:example::

    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        if ctx.invoked_subcommand is None:
            click.echo('I was invoked without subcommand')
        else:
            click.echo('I am about to invoke %s' % ctx.invoked_subcommand)

    @cli.command()
    def sync():
        click.echo('The subcommand')

그러면 실제로 다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='tool', args=[])
    invoke(cli, prog_name='tool', args=['sync'])

.. _custom-multi-commands:

새로운 다중 명령
----------------

:func:`click.group`\을 쓰는 대신 자체적으로 새로운 다중 명령을
만들 수도 있다. 필요할 때 플러그인의 명령들을 적재하는 걸
지원하려 할 때 유용하다.

새로운 다중 명령에는 나열 메소드와 적재 메소드만 구현해 주면 된다.

.. click:example::

    import click
    import os

    plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')

    class MyCLI(click.MultiCommand):

        def list_commands(self, ctx):
            rv = []
            for filename in os.listdir(plugin_folder):
                if filename.endswith('.py'):
                    rv.append(filename[:-3])
            rv.sort()
            return rv

        def get_command(self, ctx, name):
            ns = {}
            fn = os.path.join(plugin_folder, name + '.py')
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
            return ns['cli']

    cli = MyCLI(help='This tool\'s subcommands are loaded from a '
                'plugin folder dynamically.')

    if __name__ == '__main__':
        cli()

이 새 클래스를 데코레이터에 쓸 수도 있다.

.. click:example::

    @click.command(cls=MyCLI)
    def cli():
        pass

다중 명령 병합
--------------

새로운 다중 명령을 구현하는 것에 못지 않게 여러 스크립트를
하나로 합치는 것도 눈여겨볼 만하다. 일반적으로는 한쪽을
다른 쪽 아래 두는 방식을 더 권장하지만 어떤 경우에는
합치는 방식을 써서 더 편한 셸 사용 경험을 제공할 수 있다.

그런 병합 방식의 기본 구현체가 :class:`CommandCollection`
클래스다. 다른 다중 명령들의 목록을 받아서 그 명령들을
같은 단계에서 사용할 수 있게 만들어 준다.

사용례:

.. click:example::

    import click

    @click.group()
    def cli1():
        pass

    @cli1.command()
    def cmd1():
        """Command on cli1"""

    @click.group()
    def cli2():
        pass

    @cli2.command()
    def cmd2():
        """Command on cli2"""

    cli = click.CommandCollection(sources=[cli1, cli2])

    if __name__ == '__main__':
        cli()

그러면 다음처럼 된다.

.. click:run::

    invoke(cli, prog_name='cli', args=['--help'])

한 명령이 여러 곳에 존재하는 경우에는 처음 나오는 곳의 명령을 쓴다.


.. _multi-command-chaining:

다중 명령 연속 지정
-------------------

.. versionadded:: 3.0

한 번에 여러 하위 명령을 호출하는 게 가능하면 좋을 때가 있다.
예를 들어 이전에 setuptools 패키지를 설치해 본 적이 있다면
``setup.py sdist bdist_wheel upload``\라는 연속 명령에 익숙할
것이다. 이 명령은 ``sdist`` 다음에 ``bdist_wheel``\을, 그리고
``upload``\를 차례로 호출한다. 클릭 3.0부터는 이걸 아주
간편하게 구현할 수 있다. 다중 명령에 ``chain=True``\를
주기만 하면 된다.

.. click:example::

    @click.group(chain=True)
    def cli():
        pass


    @cli.command('sdist')
    def sdist():
        click.echo('sdist called')


    @cli.command('bdist_wheel')
    def bdist_wheel():
        click.echo('bdist_wheel called')

그러면 다음처럼 호출할 수 있다.

.. click:run::

    invoke(cli, prog_name='setup.py', args=['sdist', 'bdist_wheel'])

연속 다중 명령 방식을 쓸 때는 (마지막의) 한 명령에서만 인자에
``nargs=-1``\을 쓸 수 있다. 또한 연속 다중 명령 아래에 다른 다중
명령을 넣는 게 불가능하다. 그 외에는 동작 방식에 어떤 제약도 없다.
다른 경우들처럼 옵션과 인자를 받을 수 있다.

추가 참고 사항: 다중 명령에서 여러 명령을 호출할 때는
:attr:`Context.invoked_subcommand` 속성에 ``'*'`` 값이
들어가므로 별 쓸모가 없다. 이는 하위 명령 처리가 하나씩 차례로
이뤼지기 때문에 콜백 발화 때는 정확히 어떤 하위 명령들이
처리될지 알 수 없기 때문이다.

.. note::

    현재는 연속 명령들에 하위 명령을 넣는 게 불가능하다. 클릭
    향후 버전에서 고쳐질 예정이다.


다중 명령 파이프라인
--------------------

.. versionadded:: 3.0

연속 다중 명령을 사용하는 아주 흔한 경우는 한 명령이 앞 명령의
결과를 처리하게 하는 것이다. 이를 가능하게 해 주는 방법이
여러 가지 있다. 쉽게 떠오르는 걸로는 문맥 객체에 값을 저장해서
함수를 넘나들며 그 값을 처리하는 방법이 있다. 함수를
:func:`pass_context`\로 꾸며 주면 문맥 객체가 제공되므로
하위 명령에서 거기에 데이터를 저장할 수 있게 된다.

또 다른 방법은 처리 함수를 반환하게 해서 파이프라인을 구성하는
것이다. 말하자면, 하위 명령을 호출하면 거기선 매개변수들을 모두
처리하고서 어떻게 처리를 수행할지 계획을 세운다. 그러고 나면
그 처리 함수를 반환하며 돌아오는 것이다.

그럼 반환된 그 함수들은 어디로 가는 걸까? 연속 다중 명령에서는
:meth:`MultiCommand.resultcallback`\으로 콜백을 등록할 수 있는데
거기서 그 함수들을 모두 훑으며 호출한다.

좀 더 구체적으로 보자면 다음 예를 생각해 보자.

.. click:example::

    @click.group(chain=True, invoke_without_command=True)
    @click.option('-i', '--input', type=click.File('r'))
    def cli(input):
        pass

    @cli.resultcallback()
    def process_pipeline(processors, input):
        iterator = (x.rstrip('\r\n') for x in input)
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)

    @cli.command('uppercase')
    def make_uppercase():
        def processor(iterator):
            for line in iterator:
                yield line.upper()
        return processor

    @cli.command('lowercase')
    def make_lowercase():
        def processor(iterator):
            for line in iterator:
                yield line.lower()
        return processor

    @cli.command('strip')
    def make_strip():
        def processor(iterator):
            for line in iterator:
                yield line.strip()
        return processor

설명할 게 좀 많다. 하나씩 살펴보자.

1.  첫 번째로 할 일은 명령 연속 지정이 가능한 :func:`group`\을
    만드는 것이다. 그리고 하위 명령이 지정되지 않더라도 클릭에서
    호출하도록 한다. 이렇게 하지 않으면 빈 파이프라인 호출 시에
    결과 콜백을 실행하는 대신 도움말 페이지를 내놓게 된다.
2.  다음으로 할 일은 그룹에 결과 콜백을 등록하는 것이다. 그러면
    모든 하위 명령의 반환 값들, 그리고 그룹 자체가 받은 것과
    같은 키워드 매개변수들을 인자로 해서 그 콜백이 호출된다.
    즉 문맥 객체를 쓰지 않아도 거기서 입력 파일에 쉽게 접근할
    수 있다.
3.  그 결과 콜백 내에서는 입력 파일의 모든 행으로 이터레이터를
    만들고 하위 명령에서 반환한 콜백 모두를 이터레이터가 거치게
    하고서 모든 행을 stdout으로 찍는다.

이렇게 한 다음에는 원하는 대로 하위 명령들을 등록할 수 있으며
각 하위 명령에서는 행 스트림을 변경하는 처리 함수를 반환하면 된다.

주의할 점 하나는 각 콜백이 실행된 후에 클릭에서 문맥을 없앤다는
것이다. 그래서 예를 들면 파일 타입을 `processor` 함수 안에서
접근할 수 없다. 거기선 파일이 이미 닫혀 있기 때문이다.
이런 제약은 자원 관리를 훨씬 단순하게 해 주기 때문에 아마
바뀌지 않을 것이다. 따라서 파일 타입을 쓰는 대신 직접
:func:`open_file`\을 통해 파일을 열기를 권한다.

파이프라인 처리 방식도 개선한 더 복잡한 예를 클릭 저장소의
`imagepipe 연속 다중 명령 예시
<https://github.com/pallets/click/tree/master/examples/imagepipe>`__\에서
볼 수 있다. 파이프라인 기반으로 이미지 편집 툴을 구현한 것인데
내부 구조가 파이프라인에 잘 맞게 돼 있다.


기본값 바꾸기
-------------

기본적으로 매개변수의 기본값은 그 매개변수를 정의할 때 준
``default`` 플래그에서 가져오지만 거기서만 가져오는 건
아니다. 문맥의 :attr:`Context.default_map`\(딕셔너리)에서도
기본값을 가져온다. 이를 이용하면 설정 파일에서 기본값을
읽어 들여서 원래 기본값을 교체할 수 있다.

다른 패키지에서 어떤 명령들을 플러그인 형태로 가져오려는데
기본값은 마음에 들지 않을 때 유용하다.

각 하위 명령에 맞춰 필요한 대로 기본값 맵의 계층을 만들어서
스크립트 호출 시에 제공할 수 있다. 아니면 명령 어느 지점에서든
기본값을 교체할 수도 있다. 예를 들어 최상위 명령에서
설정 파일에 있는 기본값을 읽어 들일 수 있을 것이다.

사용례:

.. click:example::

    import click

    @click.group()
    def cli():
        pass

    @cli.command()
    @click.option('--port', default=8000)
    def runserver(port):
        click.echo('Serving on http://127.0.0.1:%d/' % port)

    if __name__ == '__main__':
        cli(default_map={
            'runserver': {
                'port': 5000
            }
        })

동작시켜 보면:

.. click:run::

    invoke(cli, prog_name='cli', args=['runserver'], default_map={
        'runserver': {
            'port': 5000
        }
    })

문맥 기본값
-----------

.. versionadded:: 2.0

클릭 2.0부터는 스크립트를 호출할 때만이 아니라 명령을 선언하는
데코레이터에서도 문맥의 기본값을 교체할 수 있다. 예를 들어
따로 ``default_map``\을 정의하는 앞선 예가 있을 때 그걸
데코레이터에서도 할 수 있다.

다음 예는 앞의 예와 동일하게 동작한다.

.. click:example::

    import click

    CONTEXT_SETTINGS = dict(
        default_map={'runserver': {'port': 5000}}
    )

    @click.group(context_settings=CONTEXT_SETTINGS)
    def cli():
        pass

    @cli.command()
    @click.option('--port', default=8000)
    def runserver(port):
        click.echo('Serving on http://127.0.0.1:%d/' % port)

    if __name__ == '__main__':
        cli()

마찬가지로 동작시켜 보면:

.. click:run::

    invoke(cli, prog_name='cli', args=['runserver'])


명령 반환 값
------------

.. versionadded:: 3.0

클릭 3.0에서 새로 도입된 것 중 하나는 명령 콜백 반환값을 제대로
지원하는 것이다. 이를 이용하면 이전에는 구현하기 힘들었던 여러
기능들이 가능해진다.

기본적으로 이제 어떤 명령 콜백에서도 값을 반환할 수 있다. 그
반환 값은 특정 수신자에게로 흘러간다. 이를 이용하는 사례를
:ref:`multi-command-chaining`\의 예에서 이미 보았다. 거기서
본 것처럼 반환 값들을 연속 다중 명령의 콜백에서 처리할 수 있다.

클릭에서 명령 반환 값을 다룰 때 다음 사항들에 유념해야 한다.

-   일반적으로 :meth:`BaseCommand.invoke` 메소드에서는 명령
    콜백의 반환 값이 반환된다. 이 규칙에 대한 예외는
    :class:`Group`\과 관련돼 있다.

    *   그룹에서 반환 값은 일반적으로 호출된 하위 명령의
        반환 값이다. 이 규칙의 유일한 예외로 인자 없이 호출됐고
        `invoke_without_command`\가 켜져 있으면 그룹 콜백의
        반환 값이 반환 값이다.
    *   그룹이 연속 호출 설정이 돼 있으면 모든 하위 명령
        결과들의 리스트가 반환 값이다.
    *   그룹의 반환 값을 :attr:`MultiCommand.result_callback`\을
        통해 처리할 수 있다. 연속 모드에서는 모든 반환 값들의
        리스트로, 아닌 경우에는 반환 값 하나로 호출된다.

-   :meth:`Context.invoke` 및 :meth:`Context.forward` 메소드에서
    반환 값이 솟아 나온다. 내부적으로 다른 명령을 호출하고
    싶은 경우에 유용하다.

-   클릭에선 반환 값에 대해 어떤 뚜렷한 요구 조건도 없으며 반환
    값을 자체적으로 사용하지 않는다. 그래서 반환 값을 (다중
    명령 연속 지정 예시에서와 같은) 자체 데코레이터나 처리
    흐름에서 이용하는 게 가능하다.

-   클릭 스크립트가 (:meth:`BaseCommand.main`\을 통해) 명령행
    응용으로 호출될 때는 그 반환 값이 무시된다. 단
    `standalone_mode`\가 꺼져 있는 경우에는 전달된다.
