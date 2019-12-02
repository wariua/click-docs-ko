매개변수
========

.. currentmodule:: click

클릭은 스크립트에서 두 가지 종류의 매개변수를 지원하는데,
옵션(option)과 인자(argument)다. 명령행 스크립트 작성자들 중에
이 둘을 헛갈리는 경우가 좀 있으니 차이점을 간단히 확인해 보자.
옵션은 이름 그대로 선택적이다. 인자는 일정 정도로 선택적일 수
있기는 하지만 선택적일 수 있는 방식에 훨씬 많은 제약이 있다.

옵션과 인자 중에 선택을 해야 하는 경우라면 하위 명령을 만들 때나
파일명/URL을 입력받는 경우 등에만 인자를 쓰고 그 외는 모두
옵션으로 하기를 권한다.

차이점
------

인자는 옵션보다 할 수 있는 게 적다. 다음 기능들은 옵션에서만
가능하다.

*   빠진 입력을 자동으로 묻기.
*   플래그로 동작하기. (불리언 또는 다른 방식)
*   환경 변수에서 옵션 값을 가져올 수 있음. 인자는 안 됨.
*   도움말 페이지에 옵션들은 모두 나오지만 인자는 나오지 않음.
    (이는 의도적인 것이다. 인자는 자동으로 표시하기에는 너무
    상세할 수도 있다.)

한편으로 옵션과 달리 인자로는 임의 개수의 인자를 받을 수 있다.
옵션으로는 만약 받는다면 정확히 고정된 개수(기본 1)의 인자만
받을 수 있다.

매개변수 타입
-------------

매개변수 타입으로 여러 가지가 가능하다. 다른 동작 방식의
타입을 구현할 수 있고 기본적으로 지원하는 타입도 몇 가지 있다.

``str`` / :data:`click.STRING`:
    기본 매개변수 타입이고 유니코드 문자열을 나타냄.

``int`` / :data:`click.INT`:
    정수만 받는 매개변수.

``float`` / :data:`click.FLOAT`:
    부동소수점 값만 받는 매개변수.

``bool`` / :data:`click.BOOL`:
    불리언 값을 받는 매개변수. 불리언 플래그에는 자동으로 이
    타입이 쓰인다. 문자열 값 ``1``, ``yes``, ``y``, ``t``,
    ``true``\는 `True`\로 변환되고 ``0``, ``no``, ``n``, ``f``,
    ``false``\는 `False`\로 변환된다.

:data:`click.UUID`:
    UUID 값을 받는 매개변수. 자동으로 이 타입으로 추측하지
    않으며 :class:`uuid.UUID`\로 표현한다.

.. autoclass:: File
   :noindex:

.. autoclass:: Path
   :noindex:

.. autoclass:: Choice
   :noindex:

.. autoclass:: IntRange
   :noindex:

.. autoclass:: FloatRange
  :noindex:

.. autoclass:: DateTime
   :noindex:

:class:`click.ParamType`\의 하위 클래스를 만들어서 새로운 매개변수
타입을 구현할 수 있다. 더 간단하게는 실패 시 `ValueError`\를 던지는
파이썬 함수를 전달하는 방식도 지원하지만 권하진 않는다.

.. _parameter_names:

매개변수 이름
-------------

매개변수(옵션과 인자 모두)는 정해진 수의 위치 인자들을 받으며
그 인자들은 명령 함수 매개변수로 전달된다. 대시 한 개가 있는
문자열은 짧은 인자로 추가되고 대시 두 개로 시작하는 문자열은
긴 인자로 추가된다.

대시 없이 추가하는 문자열은 내부 매개변수 이름이 되고
그 이름이 변수 이름으로도 쓰인다.

어떤 매개변수를 위한 이름들에 모두 대시가 있는 경우에는
가장 긴 인자를 골라 대시를 모두 밑줄로 바꿔서 자동으로
내부 이름을 만든다.

그리고 그 내부 이름을 소문자로 바꾼다.

예시:

* 옵션에 ``('-f', '--foo-bar')``\를 주면 매개변수 이름이 `foo_bar`\다.
* 옵션에 ``('-x',)``\를 주면 매개변수가 `x`\다.
* 옵션에 ``('-f', '--filename', 'dest')``\를 주면 매개변수 이름이 `dest`\다.
* 옵션에 ``('--CamelCaseOption',)``\을 주면 매개변수가 `camelcaseoption`\이다.
* 인자에 ``(`foogle`)``\을 주면 매개변수 이름이 `foogle`\이다.
  도움말에 표시할 읽기 좋은 다른 이름을 주려면 :ref:`doc-meta-variables`
  절을 참고하라.

새로운 타입 구현하기
--------------------

새로운 타입을 구현하려면 :class:`ParamType` 클래스의 하위 클래스를
만들어야 한다. 타입 호출 시 문맥 및 매개변수 객체가 있을 수도 있고
없을 수도 있으며, 그래서 어느 쪽도 처리할 수 있어야 한다.

다음 코드는 일반 정수에 추가로 16진수와 8진수도 받아서 보통 정수로
바꿔 주는 정수 타입을 구현한 것이다. ::

    import click

    class BasedIntParamType(click.ParamType):
        name = 'integer'

        def convert(self, value, param, ctx):
            try:
                if value[:2].lower() == '0x':
                    return int(value[2:], 16)
                elif value[:1] == '0':
                    return int(value, 8)
                return int(value, 10)
            except ValueError:
                self.fail('%s is not a valid integer' % value, param, ctx)

    BASED_INT = BasedIntParamType()

보다시피 하위 클래스에서 :meth:`ParamType.convert` 메소드를 구현해야
한다. 선택적으로 :attr:`ParamType.name` 속성을 제공할 수 있는데,
문서화 용도로만 쓰인다.
