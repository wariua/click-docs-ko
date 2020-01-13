예외 처리
=========

.. currentmodule:: click

클릭에서는 내부적으로 예외를 사용해서 응용 사용자가 일으킬 수
있는 다양한 오류 상황들을 알린다. 주로 잘못된 방식으로 사용하는
경우들이다.

어디서 오류를 처리하는가?
-------------------------

클릭에서 오류 처리는 주로 :meth:`BaseCommand.main`\에서 이뤄진다.
:exc:`ClickException`\의 모든 하위 클래스에 더해서 표준
:exc:`EOFError` 및 :exc:`KeyboardInterrupt` 예외를 처리한다.
뒤의 두 예외는 내부적으로 :exc:`Abort`\로 변환된다.

다음 로직을 적용한다.

1.  :exc:`EOFError`\나 :exc:`KeyboardInterrupt`\가 발생하면
    :exc:`Abort`\를 다시 던진다.
2.  :exc:`ClickException`\이 던져졌으면 :meth:`ClickException.show`
    메소드를 호출해서 내용을 표시한 다음
    :attr:`ClickException.exit_code`\로 프로그램을 끝낸다.
3.  :exc:`Abort` 예외가 던져졌으면 문자열  ``Aborted!``\를
    표준 오류로 찍은 다음 종료 코드 ``1``\로 프로그램을 끝낸다.
4.  다 통과했으면 종료 코드 ``0``\으로 프로그램을 끝낸다.

그렇게 하기 싫으면?
-------------------

일반적으로 언제든 :meth:`invoke` 메소드를 직접 호출할 수도
있다. 예를 들어 :class:`Command` 객체가 있다면 다음처럼
직접 호출할 수 있다. ::

    ctx = command.make_context('command-name', ['args', 'go', 'here'])
    with ctx:
        result = command.invoke(ctx)

예상할 수 있듯 이렇게 하면 예외가 전혀 처리되지 않고 튀어나오게
된다.

클릭 3.0부터는 :meth:`Command.main` 메소드를 쓰면서 단독 실행
모드를 끌 수도 있다. 그러면 예외 처리와 마지막의 암묵적
:meth:`sys.exit`\가 비활성화된다.

즉 다음처럼 할 수 있다. ::

    command.main(['command-name', 'args', 'go', 'here'],
                 standalone_mode=False)

어떤 예외들이 있는가?
---------------------

클릭에는 두 가지 베이스 예외가 있다. :exc:`ClickException`\은
클릭에서 사용자에게 알리고 싶은 모든 예외 상황에서 던진다.
그리고 :exc:`Abort`\는 클릭이 실행을 중단하도록 하는 데 쓴다.

:exc:`ClickException`\에는 :meth:`~ClickException.show` 메소드가
있어서 오류 메시지를 stderr나 주어진 파일 객체로 표시할 수 있다.
예외를 직접 사용해서 뭔가 하고 싶다면 다른 메소드나 속성이 뭐가
있는지 API 문서를 확인해 볼 수 있다.

다음 하위 클래스들을 많이 쓴다.

*   :exc:`UsageError`\로 뭔가 문제가 있음을 사용자에게 알린다.
*   :exc:`BadParameter`\로 특정 매개변수에 뭔가 문제가 있음을
    사용자에게 알린다. 많은 경우 클릭 내부에서 처리하며 가능하면
    추가 정보를 채운다. 예를 들어 콜백에서 이 예외를 던진 경우
    가능하다면 클릭에서 매개변수 이름을 자동으로 채운다.
*   :exc:`FileError`\는 클릭에서 파일을 열면서 문제가 생겼을 때
    :class:`File` 타입에서 던지는 오류다.
