.. _complex-guide:

복잡한 응용
===========

.. currentmodule:: click

클릭은 제작하려는 CLI 도구가 복잡든 단순하든 도움이 되도록 설계돼
있다. 하지만 그 설계의 강점은 명령 체계들을 원하는 대로 계층 구조로
만들 수 있다는 점에 있다. 예를 들어 Django를 써 본 적이 있다면
따로 명령행 도구가 있다는 걸 알고 있을 텐데, Celery도 마찬가지다.
그래서 Celery와 Django를 함께 사용할 때는 상호작용이 필요한
두 가지 도구가 있어서 서로에 대한 설정을 해 줘야 한다.

어느 상상의 세계에 두 가지 클릭 명령행 도구가 따로 있다면 한 명령
안에 다른 명령을 포함시켜서 이 문제를 해결할 수 있다. 예를 들면
웹 프레임워크에서 메시지 큐 프레임워크용 명령들을 함께 올릴 수 있다.

기본 개념
---------

그 동작 방식을 이해하려면 먼저 문맥과 호출 규약을 이해해야 한다.

문맥
````

클릭 명령이 실행될 때마다 :class:`Context` 객체를 만들어서
그 특정 호출을 위한 상태를 담는다. 즉 파싱 한 매개변수, 객체를
생성한 명령, 함수 종료 시 정리해야 할 자원 등을 저장해 둔다.
그리고 원한다면 응용에서 쓰는 객체도 담을 수 있다.

문맥 객체들은 최상위 객체까지 닿는 연결 리스트를 형성한다.
그리고 각 문맥은 부모 문맥으로 연결돼 있다. 그래서 어떤 명령이
다른 명령 아래에서 동작할 때 자기 문맥에 정보를 저장할 수
있으므로 부모 명령의 상태를 건드리지 않을까 염려할 필요가 없다.

하지만 부모 데이터에도 접근이 가능하기 때문에 필요하다면
사용이 가능하다.

대부분의 경우에는 문맥 객체를 볼 일이 없지만 복잡한 응용을
작성할 때는 요긴해진다. 그럼 다음 주제를 살펴볼 차례다.

호출 규약
`````````

클릭 명령 콜백이 실행될 때는 값이 지정된 매개변수들을 모두
키워드 인자로 전달받는다. 그런데 거기 빠져 있는 게 바로 문맥이다.
하지만 콜백에서 :func:`pass_context` 표시를 통해 문맥 객체를
전달받는 방식을 택할 수 있다.

그런데 콜백에서 문맥을 받는지 아닌지 모른다면 어떻게 명령
콜백을 호출할 수 있을까? 문맥 자체에서 그에 대한 처리를
해 주는 헬퍼 함수(:meth:`Context.invoke`)를 제공한다.
그 함수는 콜백을 첫 번째 인자로 받아서 올바르게 함수를 호출해
준다.

git clone 만들기
----------------

이 예시에서 우리는 어느 버전 관리 시스템을 닮은 명령행 도구를
만들려고 한다. 일반적으로 Git 같은 시스템에는 최상위 명령이
하나 있어서 몇몇 매개변수와 설정을 받고 추가로 하위 명령들이
있어서 다른 일들을 한다.

최상위 명령
```````````

모든 명령을 담을 수 있는 그룹이 최상위에 필요하다. 이 경우엔
기본 :func:`click.group`\을 사용하는데, 이를 통해 그 아래에
다른 클릭 명령들을 등록할 수 있다.

그리고 이 명령에서 도구의 상태를 설정하는 매개변수 몇 가지를
받고 싶다.

.. click:example::

    import os
    import click


    class Repo(object):
        def __init__(self, home=None, debug=False):
            self.home = os.path.abspath(home or '.')
            self.debug = debug


    @click.group()
    @click.option('--repo-home', envvar='REPO_HOME', default='.repo')
    @click.option('--debug/--no-debug', default=False,
                  envvar='REPO_DEBUG')
    @click.pass_context
    def cli(ctx, repo_home, debug):
        ctx.obj = Repo(repo_home, debug)


뭘 하는 건지 살펴보자. 일단 하위 명령을 등록할 수 있는 그룹 명령을
만든다. 그 그룹 호출 시 ``Repo`` 클래스 인스턴스를 생성하게 된다.
그 인스턴스는 이 명령행 도구를 위한 상태 정보를 담는다. 이 경우에는
몇 가지 매개변수를 저장할 뿐이지만 이 시점에서 설정 파일을
읽어 들이거나 할 수도 있다.

그리고 그 상태 객체를 문맥에 :attr:`~Context.obj`\로 저장해 둔다.
이 특별한 속성을 통해 명령에서 자식에게 전달해야 하는 것들을
기억해 둘 수 있다.

그렇게 되려면 함수에 :func:`pass_context` 표시를 해 줘야 한다.
안 그러면 문맥 객체가 완전히 감춰지게 된다.

첫 번째 자식 명령
`````````````````

첫 번째 자식 명령을 추가해 보자. clone 명령이다.

.. click:example::

    @cli.command()
    @click.argument('src')
    @click.argument('dest', required=False)
    def clone(src, dest):
        pass

clone 명령은 만들었는데, 어떻게 저장소에 접근할 수 있을까? 떠올릴
수 있는 방법 하나는 :func:`pass_context` 함수를 사용해서 저장소를
기억시켜 둔 문맥을 콜백에서 받게 하는 것이다. 하지만
:func:`pass_obj`\라는 다른 버전의 데코레이터가 있는데, 이건
저장된 객체를 (이 경우 저장소를) 전달해 준다.

.. click:example::

    @cli.command()
    @click.argument('src')
    @click.argument('dest', required=False)
    @click.pass_obj
    def clone(repo, src, dest):
        pass

끼워 넣은 명령
``````````````

지금 만들려는 프로그램과는 별 관련이 없지만 명령을 끼워 넣는 것도
꽤 잘 지원할 수 있다. 예를 들어 우리 버전 관리 시스템을 위한 완전
멋진 플러그인이 있는데 설정이 많이 필요해서 설정들을
:attr:`~Context.obj`\로 따로 저장한다고 상상해 보자. 그런데 그
명령 아래에 또 다른 명령을 붙이게 되면 아래의 명령은 느닷없이
저장소 객체 대신 플러그인 설정을 받게 된다.

이를 바로잡기 위한 확실한 방법 하나는 플러그인에서 저장소에 대한
참조를 저장하는 것일 텐데, 하지만 그렇게 하려면 명령에서 자기가
그런 플러그인 아래 붙어 있는지를 알아야 한다.

문맥이 연결돼 있다는 특성을 이용하면 훨씬 좋은 방식을 만들 수
있다. 플러그인 문맥은 저장소를 생성한 문맥에 연결돼 있다.
그렇기 때문에 문맥에 저장소 객체가 저장돼 있는 지점을 찾을
때까지 탐색을 해 볼 수 있다.

이를 위해 있는 게 클릭에 내장된 :func:`make_pass_decorator`
팩토리인데, 객체를 찾는 데코레이터를 생성해 준다. (내부적으로
:meth:`Context.find_object`\를 호출한다.) 이번 경우에선
가장 가까이 있는 ``Repo`` 객체를 찾고 싶은 거니까 다음처럼
데코레이터를 만들자.

.. click:example::

    pass_repo = click.make_pass_decorator(Repo)

이제 ``pass_obj`` 대신 ``pass_repo``\를 사용하면 항상 저장소를
받게 된다.

.. click:example::

    @cli.command()
    @click.argument('src')
    @click.argument('dest', required=False)
    @pass_repo
    def clone(repo, src, dest):
        pass

객체가 꼭 있게 하기
```````````````````

위의 예는 ``Repo`` 객체를 생성해서 문맥에 저장한 바깥 명령이
있는 경우에만 제대로 동작한다. 하지만 일부 복잡한 경우에는
이게 문제가 될 수도 있다. :func:`make_pass_decorator`\의 기본
동작은 :meth:`Context.find_object`\를 호출해서 객체를 찾는
것이다. 그런데 객체를 찾을 수 없으면
:meth:`make_pass_decorator`\가 오류를 던지게 된다. 이와 다른
동작 방식을 원하면 :meth:`Context.ensure_object`\를 쓰면
되는데, 객체를 찾아 봤는데 찾을 수 없으면 객체를 하나 생성해서
가장 가까운 문맥에 저장해 준다. :func:`make_pass_decorator`\에
``ensure=True``\를 줘도 이 동작이 켜진다.

.. click:example::

    pass_repo = click.make_pass_decorator(Repo, ensure=True)

객체가 없으면 생성한 객체를 가장 가까운 문맥에 넣는다. 그렇게
하면서 원래 거기 있던 객체를 대체하게 될 수도 있다. 그리고 이
경우엔 외부 명령을 실행하지 않더라도 여전히 명령이 실행
가능하다. 한편 이 방식이 동작하려면 그 객체 타입에 인자를
안 받는 생성자가 있어야 한다.

이제 단독으로도 돈다.

.. click:example::

    @click.command()
    @pass_repo
    def cp(repo):
        click.echo(isinstance(repo, Repo))

다음처럼 된다.

.. click:run::

    invoke(cp, [])
