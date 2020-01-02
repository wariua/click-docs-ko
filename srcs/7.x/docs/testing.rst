클릭 응용 테스트
================

.. currentmodule:: click.testing

기본적인 테스트를 위해 클릭에는 :mod:`click.testing`\이라는
모듈이 있는데, 명령행 응용을 호출하고 동작을 확인하는 걸
도와 주는 테스트 기능을 제공한다.

그 도구들은 진짜 테스트 용도로만 써야 한다. 단순함을 위해
인터프리터 상태 전반을 변경하고 전혀 스레드에 안전하지 않기
때문이다.

기본 테스트
-----------

클릭 응용 테스트를 위한 기본 기능을 제공하는 게 명령을 명령행
스크립트처럼 호출할 수 있는 :class:`CliRunner`\다.
:meth:`CliRunner.invoke` 메소드는 명령행 스크립트를 독립적으로
실행해서 그 출력을 bytes 및 이진 데이터로 캡처 한다.

결과 값은 :class:`Result` 객체인데, 캡처 한 출력 데이터,
종료 코드, 경우에 따라 예외가 담겨 있다.

예::

    import click
    from click.testing import CliRunner

    def test_hello_world():
        @click.command()
        @click.argument('name')
        def hello(name):
            click.echo('Hello %s!' % name)

        runner = CliRunner()
        result = runner.invoke(hello, ['Peter'])
        assert result.exit_code == 0
        assert result.output == 'Hello Peter!\n'

하위 명령을 테스트 하려면 :meth:`CliRunner.invoke` 메소드의 `args` 매개변수에 하위 명령 이름을 지정해 줘야 한다.

예::

    import click
    from click.testing import CliRunner
    
    def test_sync():
        @click.group()
        @click.option('--debug/--no-debug', default=False)
        def cli(debug):
            click.echo('Debug mode is %s' % ('on' if debug else 'off')) 
    
        @cli.command()
        def sync():
            click.echo('Syncing')
    
        runner = CliRunner()
        result = runner.invoke(cli, ['--debug', 'sync'])
        assert result.exit_code == 0
        assert 'Debug mode is on' in result.output
        assert 'Syncing' in result.output

``.invoke()``\에 추가로 주는 키워드 인자들은 문맥 객체를 새로 구성하는 데 쓰이게 된다. 예를 들어 어떤 고정된 터미널 폭에 대해 테스트를 돌리고 싶다면 다음처럼 할 수 있다. ::

    runner = CliRunner()
    result = runner.invoke(cli, ['--debug', 'sync'], terminal_width=60)

파일 시스템 격리
----------------

파일 시스템에 동작하는 간단한 명령행 도구에는
:meth:`CliRunner.isolated_filesystem` 메소드가 유용하다.
빈 폴더를 준비해서 현재 작업 디렉터리를 그리로 바꿔 준다.

예::

    import click
    from click.testing import CliRunner

    def test_cat():
        @click.command()
        @click.argument('f', type=click.File())
        def cat(f):
            click.echo(f.read())

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('hello.txt', 'w') as f:
                f.write('Hello World!')

            result = runner.invoke(cat, ['hello.txt'])
            assert result.exit_code == 0
            assert result.output == 'Hello World!\n'

입력 스트림
-----------

테스트 래퍼를 사용해 입력 스트림(stdin)에 입력 데이터를 제공할
수도 있다. 프롬프트를 테스트 하는 데 아주 유용하다. 예::

    import click
    from click.testing import CliRunner

    def test_prompts():
        @click.command()
        @click.option('--foo', prompt=True)
        def test(foo):
            click.echo('foo=%s' % foo)

        runner = CliRunner()
        result = runner.invoke(test, input='wau wau\n')
        assert not result.exception
        assert result.output == 'Foo: wau wau\nfoo=wau wau\n'

참고로 출력 스트림에 입력 데이터도 나오도록 프롬프트 에뮬레이션이
이뤄지게 된다. 입력을 감추도록 하면 당연히 나오지 않는다.
