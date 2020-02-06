사용자 입력 프롬프트
====================

.. currentmodule:: click

클릭에선 두 가지 위치에서 프롬프트를 지원한다. 첫째는 매개변수
처리가 이뤄질 때의 자동 프롬프트고, 둘째는 이후 독립적으로
묻는 프롬프트다.

타입에 따른 유효한 입력을 요구하는 :func:`prompt` 함수와
확인(yes/no)을 요구하는 :func:`confirm` 함수를 쓴다.

옵션 프롬프트
-------------

옵션 프롬프트는 옵션 인터페이스 내에 통합돼 있다. 자세한
내용은 :ref:`option-prompting` 참고. 내부에서 자동으로
:func:`prompt`\와 :func:`confirm` 중 필요한 쪽을 호출한다.

입력 프롬프트
-------------

사용자 입력을 수동으로 요청하는 데 :func:`prompt` 함수를
쓸 수 있다. 기본적으로 유니코드 문자열을 받지만 다른 타입을
요청할 수도 있다. 예를 들어 유효한 정수를 요청할 수 있다. ::

    value = click.prompt('Please enter a valid integer', type=int)

또한 기본값을 주는 경우에는 타입을 자동으로 결정하게 된다.
예를 들어 다음처럼 하면 실수만 받게 된다. ::

    value = click.prompt('Please enter a number', default=42.0)

확인 프롬프트
-------------

사용자가 어떤 동작을 계속 진행하려는지 묻는 데는
:func:`confirm` 함수가 요긴하다. 기본적으로 질의 결과를
불리언 값으로 반환한다. ::

    if click.confirm('Do you want to continue?'):
        click.echo('Well done!')

함수가 ``True``\를 반환하지 않는 경우 프로그램 실행을
자동으로 멈추도록 하는 동작 방식도 있다. ::

    click.confirm('Do you want to continue?', abort=True)
