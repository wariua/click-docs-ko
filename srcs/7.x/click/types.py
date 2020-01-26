import os
import stat
from datetime import datetime

from ._compat import open_stream, text_type, filename_to_ui, \
    get_filesystem_encoding, get_streerror, _get_argv_encoding, PY2
from .exceptions import BadParameter
from .utils import safecall, LazyFile


class ParamType(object):
    """Helper for converting values through types.  The following is
    necessary for a valid type:

    *   it needs a name
    *   it needs to pass through None unchanged
    *   it needs to convert from a string
    *   it needs to convert its result type through unchanged
        (eg: needs to be idempotent)
    *   it needs to be able to deal with param and context being `None`.
        This can be the case when the object is used with prompt
        inputs.
    """
    is_composite = False

    #: the descriptive name of this type
    name = None

    #: if a list of this type is expected and the value is pulled from a
    #: string environment variable, this is what splits it up.  `None`
    #: means any whitespace.  For all parameters the general rule is that
    #: whitespace splits them up.  The exception are paths and files which
    #: are split by ``os.path.pathsep`` by default (":" on Unix and ";" on
    #: Windows).
    envvar_list_splitter = None

    def __call__(self, value, param=None, ctx=None):
        if value is not None:
            return self.convert(value, param, ctx)

    def get_metavar(self, param):
        """Returns the metavar default for this param if it provides one."""

    def get_missing_message(self, param):
        """Optionally might return extra information about a missing
        parameter.

        .. versionadded:: 2.0
        """

    def convert(self, value, param, ctx):
        """Converts the value.  This is not invoked for values that are
        `None` (the missing value).
        """
        return value

    def split_envvar_value(self, rv):
        """Given a value from an environment variable this splits it up
        into small chunks depending on the defined envvar list splitter.

        If the splitter is set to `None`, which means that whitespace splits,
        then leading and trailing whitespace is ignored.  Otherwise, leading
        and trailing splitters usually lead to empty items being included.
        """
        return (rv or '').split(self.envvar_list_splitter)

    def fail(self, message, param=None, ctx=None):
        """Helper method to fail with an invalid value message."""
        raise BadParameter(message, ctx=ctx, param=param)


class CompositeParamType(ParamType):
    is_composite = True

    @property
    def arity(self):
        raise NotImplementedError()


class FuncParamType(ParamType):

    def __init__(self, func):
        self.name = func.__name__
        self.func = func

    def convert(self, value, param, ctx):
        try:
            return self.func(value)
        except ValueError:
            try:
                value = text_type(value)
            except UnicodeError:
                value = str(value).decode('utf-8', 'replace')
            self.fail(value, param, ctx)


class UnprocessedParamType(ParamType):
    name = 'text'

    def convert(self, value, param, ctx):
        return value

    def __repr__(self):
        return 'UNPROCESSED'


class StringParamType(ParamType):
    name = 'text'

    def convert(self, value, param, ctx):
        if isinstance(value, bytes):
            enc = _get_argv_encoding()
            try:
                value = value.decode(enc)
            except UnicodeError:
                fs_enc = get_filesystem_encoding()
                if fs_enc != enc:
                    try:
                        value = value.decode(fs_enc)
                    except UnicodeError:
                        value = value.decode('utf-8', 'replace')
            return value
        return value

    def __repr__(self):
        return 'STRING'


class Choice(ParamType):
    """선택 타입을 이용하면 값이 정해진 지원 값들 중 하나인지
    확인할 수 있다. 지원 값들은 모두 문자열이어야 한다.

    선택지들의 리스트나 튜플을 줘야 한다. (제너레이터 같은)
    다른 이터러블은 예상치 못한 결과를 유발할 수 있다.

    :ref:`choice-opts`\의 예시 참고.

    :param case_sensitive: 거짓으로 설정하면 선택지들이
        대소문자 구분이 없게 됨. 기본은 참.
    """

    name = 'choice'

    def __init__(self, choices, case_sensitive=True):
        self.choices = choices
        self.case_sensitive = case_sensitive

    def get_metavar(self, param):
        return '[%s]' % '|'.join(self.choices)

    def get_missing_message(self, param):
        return 'Choose from:\n\t%s.' % ',\n\t'.join(self.choices)

    def convert(self, value, param, ctx):
        # Exact match
        if value in self.choices:
            return value

        # Match through normalization and case sensitivity
        # first do token_normalize_func, then lowercase
        # preserve original `value` to produce an accurate message in
        # `self.fail`
        normed_value = value
        normed_choices = self.choices

        if ctx is not None and \
           ctx.token_normalize_func is not None:
            normed_value = ctx.token_normalize_func(value)
            normed_choices = [ctx.token_normalize_func(choice) for choice in
                              self.choices]

        if not self.case_sensitive:
            normed_value = normed_value.lower()
            normed_choices = [choice.lower() for choice in normed_choices]

        if normed_value in normed_choices:
            return normed_value

        self.fail('invalid choice: %s. (choose from %s)' %
                  (value, ', '.join(self.choices)), param, ctx)

    def __repr__(self):
        return 'Choice(%r)' % list(self.choices)


class DateTime(ParamType):
    """DateTime 타입은 날짜 문자열을 `datetime` 객체로 변환한다.

    확인할 형식 문자열들을 설정할 수 있으며 몇 가지 많이 쓰는
    (시간대 없는) ISO 8601 형식들이 기본값이다.

    *DateTime* 형식을 지정할 때 리스트나 튜플을 줘야 한다.
    제너레이터 같은 다른 이터러블은 예상치 못한 결과를 유발할 수 있다.

    형식 문자열들은 ``datetime.strptime``\으로 처리되며, 그에 따라
    허용되는 형식 문자열이 규정된다.

    각 형식을 차례대로 사용해 파싱을 시도하며 파싱이 성공한 첫 번째
    형식을 쓴다.

    :param formats: 시도 순서대로 된 날짜 형식 문자열들의 리스트
                    또는 튜플. 기본값은
                    ``'%Y-%m-%d'``, ``'%Y-%m-%dT%H:%M:%S'``,
                    ``'%Y-%m-%d %H:%M:%S'``.
    """
    name = 'datetime'

    def __init__(self, formats=None):
        self.formats = formats or [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S'
        ]

    def get_metavar(self, param):
        return '[{}]'.format('|'.join(self.formats))

    def _try_to_convert_date(self, value, format):
        try:
            return datetime.strptime(value, format)
        except ValueError:
            return None

    def convert(self, value, param, ctx):
        # Exact match
        for format in self.formats:
            dtime = self._try_to_convert_date(value, format)
            if dtime:
                return dtime

        self.fail(
            'invalid datetime format: {}. (choose from {})'.format(
                value, ', '.join(self.formats)))

    def __repr__(self):
        return 'DateTime'


class IntParamType(ParamType):
    name = 'integer'

    def convert(self, value, param, ctx):
        try:
            return int(value)
        except (ValueError, UnicodeError):
            self.fail('%s is not a valid integer' % value, param, ctx)

    def __repr__(self):
        return 'INT'


class IntRange(IntParamType):
    """:data:`click.INT`\와 비슷하게 동작하되 값을 어떤 범위로
    제약하는 매개변수. 값이 범위를 벗어날 때 기본 동작은 실패하는
    것이지만 두 경곗값 중 하나로 조용히 자를 수도 있다.

    :ref:`ranges`\의 예시 참고.
    """
    name = 'integer range'

    def __init__(self, min=None, max=None, clamp=False):
        self.min = min
        self.max = max
        self.clamp = clamp

    def convert(self, value, param, ctx):
        rv = IntParamType.convert(self, value, param, ctx)
        if self.clamp:
            if self.min is not None and rv < self.min:
                return self.min
            if self.max is not None and rv > self.max:
                return self.max
        if self.min is not None and rv < self.min or \
           self.max is not None and rv > self.max:
            if self.min is None:
                self.fail('%s is bigger than the maximum valid value '
                          '%s.' % (rv, self.max), param, ctx)
            elif self.max is None:
                self.fail('%s is smaller than the minimum valid value '
                          '%s.' % (rv, self.min), param, ctx)
            else:
                self.fail('%s is not in the valid range of %s to %s.'
                          % (rv, self.min, self.max), param, ctx)
        return rv

    def __repr__(self):
        return 'IntRange(%r, %r)' % (self.min, self.max)


class FloatParamType(ParamType):
    name = 'float'

    def convert(self, value, param, ctx):
        try:
            return float(value)
        except (UnicodeError, ValueError):
            self.fail('%s is not a valid floating point value' %
                      value, param, ctx)

    def __repr__(self):
        return 'FLOAT'


class FloatRange(FloatParamType):
    """:data:`click.FLOAT`\과 비슷하게 동작하되 값을 어떤 범위로
    제약하는 매개변수. 값이 범위를 벗어날 때 기본 동작은 실패하는
    것이지만 두 경곗값 중 하나로 조용히 자를 수도 있다.

    :ref:`ranges`\의 예시 참고.
    """
    name = 'float range'

    def __init__(self, min=None, max=None, clamp=False):
        self.min = min
        self.max = max
        self.clamp = clamp

    def convert(self, value, param, ctx):
        rv = FloatParamType.convert(self, value, param, ctx)
        if self.clamp:
            if self.min is not None and rv < self.min:
                return self.min
            if self.max is not None and rv > self.max:
                return self.max
        if self.min is not None and rv < self.min or \
           self.max is not None and rv > self.max:
            if self.min is None:
                self.fail('%s is bigger than the maximum valid value '
                          '%s.' % (rv, self.max), param, ctx)
            elif self.max is None:
                self.fail('%s is smaller than the minimum valid value '
                          '%s.' % (rv, self.min), param, ctx)
            else:
                self.fail('%s is not in the valid range of %s to %s.'
                          % (rv, self.min, self.max), param, ctx)
        return rv

    def __repr__(self):
        return 'FloatRange(%r, %r)' % (self.min, self.max)


class BoolParamType(ParamType):
    name = 'boolean'

    def convert(self, value, param, ctx):
        if isinstance(value, bool):
            return bool(value)
        value = value.lower()
        if value in ('true', 't', '1', 'yes', 'y'):
            return True
        elif value in ('false', 'f', '0', 'no', 'n'):
            return False
        self.fail('%s is not a valid boolean' % value, param, ctx)

    def __repr__(self):
        return 'BOOL'


class UUIDParameterType(ParamType):
    name = 'uuid'

    def convert(self, value, param, ctx):
        import uuid
        try:
            if PY2 and isinstance(value, text_type):
                value = value.encode('ascii')
            return uuid.UUID(value)
        except (UnicodeError, ValueError):
            self.fail('%s is not a valid UUID value' % value, param, ctx)

    def __repr__(self):
        return 'UUID'


class File(ParamType):
    """매개변수를 읽기 또는 쓰기용 파일로 선언한다. 그 파일은 (명령
    동작이 완료된 후) 문맥이 없어지면 자동으로 닫힌다.

    파일을 읽기 또는 쓰기용으로 열 수 있다. 특수 값 ``-``\는
    모드에 따라 stdin이나 stdout을 나타낸다.

    기본적으로는 파일이 텍스트 읽기용으로 열리지만 바이너리 모드나
    쓰기용으로 열 수도 있다. 그리고 encoding 매개변수를 써서 특정
    인코딩을 강제할 수 있다.

    ``lazy`` 플래그는 파일을 즉시 열지 아니면 첫 IO에서 열지를 제어한다.
    기본 방식은 표준 입력 및 출력 스트림, 그리고 읽기용으로 여는 파일은
    즉시 열고 그 외는 늦게 여는 것이다. 파일을 읽기용으로 늦게 열 때는
    확인을 위해 잠깐 열기는 하되 첫 IO까지 열어두지 않는다. 늦게 여는
    동작이 유용한 건 쓰기용으로 열면서 필요할 때까지는 파일이 생성되지
    않게 할 때이다.

    클릭 2.0부터는 파일을 원자적으로 열 수도 있는데, 그렇게 하면
    모든 쓰기 내용이 같은 폴더 내의 별도 파일로 가며 작업이 끝나면
    그 파일이 원래 위치로 옮겨지게 된다. 다른 사용자들이 규칙적으로
    읽는 파일을 변경하는 경우에 유용하다.

    더 자세한 내용은 :ref:`file-args` 참고.
    """
    name = 'filename'
    envvar_list_splitter = os.path.pathsep

    def __init__(self, mode='r', encoding=None, errors='strict', lazy=None,
                 atomic=False):
        self.mode = mode
        self.encoding = encoding
        self.errors = errors
        self.lazy = lazy
        self.atomic = atomic

    def resolve_lazy_flag(self, value):
        if self.lazy is not None:
            return self.lazy
        if value == '-':
            return False
        elif 'w' in self.mode:
            return True
        return False

    def convert(self, value, param, ctx):
        try:
            if hasattr(value, 'read') or hasattr(value, 'write'):
                return value

            lazy = self.resolve_lazy_flag(value)

            if lazy:
                f = LazyFile(value, self.mode, self.encoding, self.errors,
                             atomic=self.atomic)
                if ctx is not None:
                    ctx.call_on_close(f.close_intelligently)
                return f

            f, should_close = open_stream(value, self.mode,
                                          self.encoding, self.errors,
                                          atomic=self.atomic)
            # If a context is provided, we automatically close the file
            # at the end of the context execution (or flush out).  If a
            # context does not exist, it's the caller's responsibility to
            # properly close the file.  This for instance happens when the
            # type is used with prompts.
            if ctx is not None:
                if should_close:
                    ctx.call_on_close(safecall(f.close))
                else:
                    ctx.call_on_close(safecall(f.flush))
            return f
        except (IOError, OSError) as e:
            self.fail('Could not open file: %s: %s' % (
                filename_to_ui(value),
                get_streerror(e),
            ), param, ctx)


class Path(ParamType):
    """경로 타입은 :class:`File` 타입과 비슷하되 다른 검사들을
    수행한다. 우선 열린 파일 핸들을 반환하는 게 아니라 그냥 파일명을
    반환한다. 그리고 그 파일 내지 디렉터리가 어떠해야 하는가에 대한
    다양한 기본 검사를 수행할 수 있다.

    .. versionchanged:: 6.0
       `allow_dash` 추가됨.

    :param exists: 참으로 설정 시 이 값이 유효하려면 파일 내지
                   디렉터리가 존재해야 함. 이 조건을 지정하지 않고
                   파일이 실재 존재하지 않으면 이후 검사를 모두
                   조용히 건너뛴다.
    :param file_okay: 파일이 가능한 값인지 여부를 지정.
    :param dir_okay: 디렉터리가 가능한 값인지 여부를 지정.
    :param writable: 참이면 쓰기 가능 여부 검사를 수행.
    :param readable: 참이면 읽기 가능 여부 검사를 수행.
    :param resolve_path: 참이면 경로를 완전히 해석하고 나서 값을
                         계속 전달함. 즉 절대 경로가 되고 심볼릭
                         링크들을 해석한다. 물결표 확장은 셸에서
                         할 일이므로 하지 않는다.
    :param allow_dash: `True`\로 설정 시 대시 하나로 표준 스트림을
                       나타내는 걸 허용함.
    :param path_type: 선택적. 경로를 나타내는 데 사용해야 할
                      문자열 타입. 기본은 `None`\으로, 클릭에서
                      처리하는 입력 데이터가 어느 쪽에 맞는가에
                      따라 반환 값이 bytes 아니면 unicode가 된다.
    """
    envvar_list_splitter = os.path.pathsep

    def __init__(self, exists=False, file_okay=True, dir_okay=True,
                 writable=False, readable=True, resolve_path=False,
                 allow_dash=False, path_type=None):
        self.exists = exists
        self.file_okay = file_okay
        self.dir_okay = dir_okay
        self.writable = writable
        self.readable = readable
        self.resolve_path = resolve_path
        self.allow_dash = allow_dash
        self.type = path_type

        if self.file_okay and not self.dir_okay:
            self.name = 'file'
            self.path_type = 'File'
        elif self.dir_okay and not self.file_okay:
            self.name = 'directory'
            self.path_type = 'Directory'
        else:
            self.name = 'path'
            self.path_type = 'Path'

    def coerce_path_result(self, rv):
        if self.type is not None and not isinstance(rv, self.type):
            if self.type is text_type:
                rv = rv.decode(get_filesystem_encoding())
            else:
                rv = rv.encode(get_filesystem_encoding())
        return rv

    def convert(self, value, param, ctx):
        rv = value

        is_dash = self.file_okay and self.allow_dash and rv in (b'-', '-')

        if not is_dash:
            if self.resolve_path:
                rv = os.path.realpath(rv)

            try:
                st = os.stat(rv)
            except OSError:
                if not self.exists:
                    return self.coerce_path_result(rv)
                self.fail('%s "%s" does not exist.' % (
                    self.path_type,
                    filename_to_ui(value)
                ), param, ctx)

            if not self.file_okay and stat.S_ISREG(st.st_mode):
                self.fail('%s "%s" is a file.' % (
                    self.path_type,
                    filename_to_ui(value)
                ), param, ctx)
            if not self.dir_okay and stat.S_ISDIR(st.st_mode):
                self.fail('%s "%s" is a directory.' % (
                    self.path_type,
                    filename_to_ui(value)
                ), param, ctx)
            if self.writable and not os.access(value, os.W_OK):
                self.fail('%s "%s" is not writable.' % (
                    self.path_type,
                    filename_to_ui(value)
                ), param, ctx)
            if self.readable and not os.access(value, os.R_OK):
                self.fail('%s "%s" is not readable.' % (
                    self.path_type,
                    filename_to_ui(value)
                ), param, ctx)

        return self.coerce_path_result(rv)


class Tuple(CompositeParamType):
    """클릭의 기본 동작은 각 값에 바로 타입을 적용하는 것이다.
    대부분 경우에는 잘 동작하지만 `nargs`\가 어떤 정해진 개수이고
    항목마다 다른 타입을 써야 할 때는 예외이다. 그때는
    :class:`Tuple` 타입을 쓸 수 있다. 이 타입은 `nargs`\를 고정
    개수로 설정한 경우에만 쓸 수 있다.

    자세한 내용은 :ref:`tuple-type` 참고.

    type으로 파이썬 튜플 리터럴을 쓰면 이 타입을 선택할 수 있다.

    :param types: 튜플 항목들에 쓸 타입들의 리스트.
    """

    def __init__(self, types):
        self.types = [convert_type(ty) for ty in types]

    @property
    def name(self):
        return "<" + " ".join(ty.name for ty in self.types) + ">"

    @property
    def arity(self):
        return len(self.types)

    def convert(self, value, param, ctx):
        if len(value) != len(self.types):
            raise TypeError('It would appear that nargs is set to conflict '
                            'with the composite type arity.')
        return tuple(ty(x, param, ctx) for ty, x in zip(self.types, value))


def convert_type(ty, default=None):
    """Converts a callable or python ty into the most appropriate param
    ty.
    """
    guessed_type = False
    if ty is None and default is not None:
        if isinstance(default, tuple):
            ty = tuple(map(type, default))
        else:
            ty = type(default)
        guessed_type = True

    if isinstance(ty, tuple):
        return Tuple(ty)
    if isinstance(ty, ParamType):
        return ty
    if ty is text_type or ty is str or ty is None:
        return STRING
    if ty is int:
        return INT
    # Booleans are only okay if not guessed.  This is done because for
    # flags the default value is actually a bit of a lie in that it
    # indicates which of the flags is the one we want.  See get_default()
    # for more information.
    if ty is bool and not guessed_type:
        return BOOL
    if ty is float:
        return FLOAT
    if guessed_type:
        return STRING

    # Catch a common mistake
    if __debug__:
        try:
            if issubclass(ty, ParamType):
                raise AssertionError('Attempted to use an uninstantiated '
                                     'parameter type (%s).' % ty)
        except TypeError:
            pass
    return FuncParamType(ty)


#: A dummy parameter type that just does nothing.  From a user's
#: perspective this appears to just be the same as `STRING` but internally
#: no string conversion takes place.  This is necessary to achieve the
#: same bytes/unicode behavior on Python 2/3 in situations where you want
#: to not convert argument types.  This is usually useful when working
#: with file paths as they can appear in bytes and unicode.
#:
#: For path related uses the :class:`Path` type is a better choice but
#: there are situations where an unprocessed type is useful which is why
#: it is is provided.
#:
#: .. versionadded:: 4.0
UNPROCESSED = UnprocessedParamType()

#: A unicode string parameter type which is the implicit default.  This
#: can also be selected by using ``str`` as type.
STRING = StringParamType()

#: An integer parameter.  This can also be selected by using ``int`` as
#: type.
INT = IntParamType()

#: A floating point value parameter.  This can also be selected by using
#: ``float`` as type.
FLOAT = FloatParamType()

#: A boolean parameter.  This is the default for boolean flags.  This can
#: also be selected by using ``bool`` as a type.
BOOL = BoolParamType()

#: A UUID parameter.
UUID = UUIDParameterType()
