Bash 완성 기능
==============

.. versionadded:: 2.0

클릭 2.0부터는 모든 클릭 스크립트에 대한 Bash 완성 지원이
내장돼 있다. 완성 기능을 사용할 수 있는 경우에 대한 어떤 제약이
있기는 하지만 대부분은 바로 동작할 것이다.

제약 사항
---------

스크립트가 제대로 설치돼 있고 ``python`` 명령을 통해 실행되는
게 아닐 때만 Bash 완성 기능을 쓸 수 있다. 설치 방법에 대해선
:ref:`setuptools-integration` 절을 보라. 클릭에서는 현재
Bash 및 Zsh의 완성 기능만 지원한다.

완성 대상
---------

일반적으로 말해 Bash 완성 지원은 하위 명령, 옵션, 그리고
타입이 click.Choice인 옵션 및 인자의 값을 완성하게 된다.
하위 명령과 선택 값들은 항상 나열하는 반면 옵션은 대시를 최소
하나 준 경우에만 보여 준다. 예::

    $ repo <TAB><TAB>
    clone    commit   copy     delete   setuser
    $ repo clone -<TAB><TAB>
    --deep     --help     --rev      --shallow  -r

추가로 인자와 옵션에 ``autocompletion`` 매개변수를 줘서 다른
내용을 제안할 수도 있다. ``autocompletion``\은 문자열
리스트를 반환하는 콜백 함수여야 한다. 제안 목록을 Bash
완성 시점에 동적으로 생성해야 할 때 유용하다. 콜백 함수는
키워드 인자 3개를 받게 된다.

- ``ctx`` - 현재 클릭 문맥.
- ``args`` - 받은 인자들 목록.
- ``incomplete`` - 완성 중인 부분 단어 문자열.
  아직 문자를 입력하지 않았으면 빈 문자열 ``''``\일 수도 있다.

다음은 콜백 함수를 써서 동적으로 제안 목록을 만들어 내는 예이다.

.. click:example::

    import os

    def get_env_vars(ctx, args, incomplete):
        return [k for k in os.environ.keys() if incomplete in k]

    @click.command()
    @click.argument("envvar", type=click.STRING, autocompletion=get_env_vars)
    def cmd1(envvar):
        click.echo('환경 변수: %s' % envvar)
        click.echo('값: %s' % os.environ[envvar])


완성 도움말 문자열 (ZSH 한정)
-----------------------------

ZSH에서는 완성 항목에 대한 도움말 문자열을 보여 주는 걸 지원한다.
옵션과 하위 명령의 도움말 매개변수에서 그 문자열들을 얻는다.
동적으로 완성 항목을 생성하는 경우에는 문자열 대신 튜플을 반환해서
도움말 문자열을 제공할 수 있다. 튜플의 첫 항목이 완성 문자열이고
두 번째가 표시할 도움말 문자열이다.

다음은 콜백 함수를 써서 동적으로 도움말 문자열이 있는 제안 목록을 만들어 내는 예이다.

.. click:example::

    import os

    def get_colors(ctx, args, incomplete):
        colors = [('red', '빨간색에 대한 도움말 문자열'),
                  ('blue', '파란색에 대한 도움말 문자열'),
                  ('green', '녹색에 대한 도움말 문자열')]
        return [c for c in colors if incomplete in c[0]]

    @click.command()
    @click.argument("color", type=click.STRING, autocompletion=get_colors)
    def cmd1(color):
        click.echo('선택한 색상: %s' % color)


활성화
------

Bash 완성을 활성화하려면 스크립트에 완성 기능을 사용할 수 있다는
걸 Bash에게 알려 줘야 하며, 완성 방법도 알려 줘야 한다. 모든 클릭
응용에는 그에 대한 지원이 기본으로 포함돼 있다. 일반적으로
``_<PROG_NAME>_COMPLETE``\이라는 특수 환경 변수를 통해 동작하게
되는데, 여기서 ``<PROG_NAME>``\은 응용 실행 파일 이름을 대문자로
하고 대시를 밑줄로 바꾼 것이다.

작성한 도구 이름이 ``foo-bar``\라면 특수 변수 이름은
``_FOO_BAR_COMPLETE``\이다. 이 변수를 ``source`` 값으로
내보이면 활성화 스크립트를 내놓게 되므로 간단히 활성화할 수 있다.

예를 들어 ``foo-bar`` 스크립트에 대해 Bash 완성을 켜고 싶다면
``.bashrc``\에 다음을 넣어 주면 된다. ::

    eval "$(_FOO_BAR_COMPLETE=source foo-bar)"

zsh 사용자라면 ``.zshrc``\에 다음을 추가하면 된다. ::

    eval "$(_FOO_BAR_COMPLETE=source_zsh foo-bar)"

그러면 이제 스크립트에 자동 완성이 켜지게 된다.

활성화 스크립트
---------------

위의 활성화 예시에서는 셸 시작 때마다 응용을 호출하게 된다.
따라서 응용 수가 많으면 셸이 뜨는 게 상당히 느려질 수도 있다.
그렇게 하는 대신 그 내용물을 담은 파일을 제공할 수도 있을
텐데, Git과 여타 시스템에서 그렇게 하고 있다.

간단히 가능하다. ::

    _FOO_BAR_COMPLETE=source foo-bar > foo-bar-complete.sh

zsh인 경우::

    _FOO_BAR_COMPLETE=source_zsh foo-bar > foo-bar-complete.sh

그러고 나선 .bashrc나 .zshrc에 다음을 대신 넣어 주게 된다. ::

    . /path/to/foo-bar-complete.sh


