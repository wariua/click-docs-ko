파이썬 3 지원
=============

.. currentmodule:: click

클릭이 파이썬 3를 지원하긴 하지만 다른 명령행 도구 라이브러리들과
마찬가지로 파이썬 3 유니코드 텍스트 모델의 문제를 겪는다. 이 문서
내의 모든 예시들은 파이썬 2.x와 파이썬 3.4 이상에서 돌 수 있도록
작성됐다.

현재로선 파이썬 3가 필수가 아니라면 클릭 도구들에 파이썬 2를
쓰기를 강력히 권장한다.

.. _python3-limitations:

파이썬 3에서의 제약 사항
------------------------

현재 클릭은 파이썬 3에서 다음 문제를 겪는다.

*   전통적으로 유닉스에서 명령행은 유니코드가 아니라 바이트다.
    이와 관련해 인코딩 힌트가 있기는 하지만 일반적으로 안 통하는
    경우가 있을 수 있다. 가장 흔하게는 다른 로캘을 쓰는 머신으로
    SSH 연결을 할 때가 그렇다.

    현재는 환경을 잘못 구성하면 양방향 변환 surrogate 이스케이프
    지원 결여 때문에 파이썬 3에서 광범위한 유니코드 문제를 유발할
    수 있다. 이건 클릭 자체에선 고칠 수 없다.

    자세한 내용은 :ref:`python3-surrogates` 참고.

*   파이썬 3에서는 기본적으로 표준 입력과 표준 출력을 유니코드
    모드로 연다. 그래서 특정 상황에서는 스트림을 이진 모드로
    다시 열어야 한다. 그런데 그렇게 하는 표준적인 방법이 없기
    때문에 항상 잘 동작하지는 않을 수도 있다. 주로 명령행
    응용을 테스트 할 때 문제가 될 수 있다.

    다음은 지원되지 않는다. ::

        sys.stdin = io.StringIO('Input here')
        sys.stdout = io.StringIO()

    대신 다음처럼 해야 한다. ::

        input = 'Input here'
        in_stream = io.BytesIO(input.encode('utf-8'))
        sys.stdin = io.TextIOWrapper(in_stream, encoding='utf-8')
        out_stream = io.BytesIO()
        sys.stdout = io.TextIOWrapper(out_stream, encoding='utf-8')

    이 경우에 버퍼 내용물에 접근하고 싶다면 ``sys.stdout.getvalue()``\가
    아니라 ``out_stream.getvalue()``\를 써야 한다. 래퍼가 그
    메소드를 전달해 주지 않기 때문이다.

파이썬 2와 3에서의 차이점
-------------------------

클릭에서는 파이썬 2와 파이썬 3에 대해 다음 규칙을 따름으로써
둘의 차이를 가급적 줄이고자 한다.

파이썬 2에서는 다음과 같다.

*   ``sys.stdin``, ``sys.stdout``, ``sys.stderr``\가 이진 모드로
    열리지만 일부 경우에 유니코드 출력을 지원한다. 클릭은 이를
    뒤엎으려 하지 않으며 스트림을 유니코드 기반으로 만드는 방법을
    제공한다.
*   ``sys.argv``\가 항상 바이트 기반이다. 클릭에서는 모든 입력
    타입에 bytes를 주며 필요하면 변환을 한다. :class:`STRING`
    타입에서는 자동으로 적합한 인코딩들을 시도해서 입력값을
    자동으로 문자열로 바꾸게 된다.
*   파일을 다룰 때 클릭에서는 절대 유니코드 API를 거치지 않고
    운영 체제의 바이트 API를 사용해서 파일을 열게 된다.

파이썬 3에서는 다음과 같다.

*   ``sys.stdin``, ``sys.stdout``, ``sys.stderr``\가 기본적으로
    텍스트 기반이다. 클릭에서 이진 스트림이 필요할 때는 하위
    이진 스트림을 얻으려고 시도한다. 어떻게 그렇게 하는지는
    :ref:`python3-limitations` 참고.
*   ``sys.argv``\가 항상 유니코드 기반이다. 즉 클릭 내 타입들의
    입력값의 네이티브 타입이 바이트가 아니라 유니코드다.

    터미널이 잘못 설정돼 있고 파이썬에서 인코딩을 알아낼 수
    없을 때 문제가 발생한다.  그 경우 유니코드 문자열은 surrogate
    이스케이프로 인코딩 된 잘못된 바이트들을 담게 된다.
*   파일을 다룰 때 클릭에서는 항상 유니코드 파일 시스템 API
    호출을 사용하며 운영 체제가 알려 주었거나 추측한 파일 시스템
    인코딩을 쓰게 된다. 파일명에 surrogate를 지원하므로 환경이
    잘못 구성됐더라도 :class:`File` 타입을 통해 파일을 여는 게
    가능할 것이다.

.. _python3-surrogates:

파이썬 3 surrogate 문자 처리
----------------------------

클릭을 파이썬 3로 돌릴 때는 모든 유니코드 처리가 표준 라이브러리
내에서 이뤄지고 그래서 그 동작 방식에 영향을 받는다. 반면
파이썬 2에서는 유니코드 처리를 모두 클릭 자체에서 하며, 그래서
오류 처리 방식에 차이가 생긴다.

가장 눈에 띄는 차이는 파이썬 2에서는 유니코드가 "그냥 동작"하는
데 반해 파이썬 3에서는 추가로 신경 쓸 게 있다는 점이다. 그 이유는
파이썬 3에서 인코딩 탐지가 인터프리터 내에서 이뤄지며 리눅스와
몇몇 다른 운영 체제에서 인코딩 처리에 문제가 있기 때문이다.

가장 문제가 되는 건 클릭 스크립트를 init 시스템(sysvinit, upstart,
systemd 등)이나 설치 도구(salt, puppet), 크론 작업(cron)에서
호출할 때 유니코드 로캘을 export 하지 않으면 동작을 거부한다는
점이다.

그런 상황에서 클릭은 더 이상의 실행을 막아서 로캘을 설정할 수밖에
없도록 한다. 이렇게 하는 이유는 일단 호출이 되고 나면 시스템의
상태에 대해 알 수가 없으므로 파이썬의 유니코드 처리가 동작하기
전에 그 값들을 복원할 수 없기 때문이다.

파이썬 3에서 다음 오류와 비슷한 걸 보게 된다면::

    Traceback (most recent call last):
      ...
    RuntimeError: Click will abort further execution because Python 3 was
      configured to use ASCII as encoding for the environment. Either switch
      to Python 2 or consult the Python 3 section of the docs for
      mitigation steps.

파이썬 3에서 보기에 ASCII 데이터만 가능한 상황이라는 뜻이다.
이 문제에 대한 해법은 컴퓨터가 어떤 로캘로 돌고 있는지에 따라
다르다.

예를 들어 독일에서 쓰는 리눅스 머신이라면 로캘을
``de_DE.utf-8``\로 내보내서 문제를 고칠 수 있다. ::

    export LC_ALL=de_DE.utf-8
    export LANG=de_DE.utf-8

미국의 머신이라면 ``en_US.utf-8``\을 쓰면 된다. 일부 최신 리눅스
시스템에서는 로캘로 ``C.UTF-8``\을 써 볼 수도 있다. ::

    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8

일부 시스템에서는 `UTF-8`\을 `UTF8`\로 써야 한다고 하고 반대인
경우도 있다고 한다. 지원되는 로캘을 보려면 ``locale -a``\를
실행하면 된다. ::

    locale -a

파이썬 스크립트를 호출하기 전에 이렇게 해야 한다. 이유가
궁금하다면 파이썬 3 버그 트래커의 논의에 참여해 볼 수 있다.

*   `ASCII is a bad filesystem default encoding
    <http://bugs.python.org/issue13643#msg149941>`_
*   `Use surrogateescape as default error handler
    <http://bugs.python.org/issue19977>`_
*   `Python 3 raises Unicode errors in the C locale
    <http://bugs.python.org/issue19846>`_
*   `LC_CTYPE=C:  pydoc leaves terminal in an unusable state
    <http://bugs.python.org/issue21398>`_ (페이저 지원을 stdlib의
    pydoc 모듈로 제공하므로 클릭과 관련 있음.)

유니코드 리터럴
---------------

클릭 5.0부터 파이썬 2에서 ``unicode_literals`` future 임포트를
쓰면 경고를 한다. 그 임포트로 인해 유니코드 데이터를 다루지
못하는 API에 유니코드가 들어가면서 의도치 않게 버그를 유발할
수 있다는 점을 경고하는 것이다. 문제 사례를 보고 싶다면
github 이슈 `python-future#22
<https://github.com/PythonCharmers/python-future/issues/22>`_\의
논의 참고.

클릭 명령이 정의돼 있거나 클릭 명령을 호출하는 어느 파일에서든
``unicode_literals``\를 쓰면 경고를 받게 된다.
``unicode_literals``\를 사용하지 말고 대신 유니코드 문자열에
명시적으로 ``u`` 접두사를 쓰기를 강력히 권한다.

그 경고를 무시하고서 위험을 감수하고 ``unicode_literals``\를
쓰고 싶다면 다음처럼 해서 경고를 끌 수 있다. ::

    import click
    click.disable_unicode_literals_warning = True
