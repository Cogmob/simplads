from enum import Enum
from simplads.simplad_monad.delta_type import DeltaType
from simplads.simplad_monad.namedtuples.bind_args import BindArgs
from simplads.simplad_monad.namedtuples.delta_overwrite import DeltaOverwrite
from simplads.simplad_monad.simplad_base_helper import SimpladBaseHelper
from .namedtuples.error_res import ErrorRes
import abc

# delta: [messages], {new_listeners}, return_messages
# annotation_wrapper: is_default, {listeners}

# bind (func)(i) return (annotation_wrapper, unbound), higher_deltas
# unit(i) returns annotation_wrapper, unbound

class ErrorSimplad(SimpladBaseHelper):
    @staticmethod
    def initial_annotation(unbound):
        return ErrorType.none

    @staticmethod
    # returns Bound(unbound, higher_deltas)
    def run(func, annotation, unbound, higher_deltas):
        if annotation is ErrorType.none:
            return func(BindArgs(bound=unbound, deltas=higher_deltas))
        return BindArgs(bound=unbound, deltas=higher_deltas)

    @staticmethod
    # returns annotation, overwrite_unbound
    def apply_delta(annotation, delta, unbound):
        if delta[0] is ErrorType.none:
            return delta[0], DeltaOverwrite()
        if delta[0] is ErrorType.error:
            return delta[0], DeltaOverwrite(
                overwrite=True,
                new_value=ErrorRes(has_error=True, error_text=delta[1], result=unbound))
        return delta[0], DeltaOverwrite(
            overwrite=True,
            new_value=ErrorRes(has_error=False, result=unbound))

    @staticmethod
    def merge_deltas(a, b):
        if a is ErrorType.error:
            return a
        return b

class ErrorType(Enum):
    error = 1
    none = 2
    finish = 3

class ErrorDeltaMaker():
    @staticmethod
    def error(i):
        return [ErrorType.error, i]

    @staticmethod
    def no_error():
        return [ErrorType.none]

    @staticmethod
    def finish():
        return [ErrorType.finish]
