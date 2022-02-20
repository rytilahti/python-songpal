"""Presentation of an API method."""
import json
import logging
from pprint import pformat as pf
from typing import Dict, Union

import attr

from .common import SongpalException

_LOGGER = logging.getLogger(__name__)


@attr.s
class MethodSignature:
    """Method signature."""

    @staticmethod
    def return_type(x: str) -> Union[type, str]:
        """Return a python type for a string presentation if possible."""
        if x == "string":
            return str
        if x == "Boolean":
            return bool
        if x == "int":
            return int

        return x

    @staticmethod
    def parse_json_types(x) -> Union[type, str, Dict[str, type]]:
        """Parse JSON signature. Used to parse input and output parameters."""
        try:
            if x.endswith("*"):  # TODO handle arrays properly
                # _LOGGER.debug("got an array %s: %s" % (self.name, x))
                x = x.rstrip("*")

            obj = json.loads(x)
            obj = {x: MethodSignature.return_type(obj[x]) for x in obj}
        except json.JSONDecodeError as ex:
            try:
                return MethodSignature.return_type(x)
            except Exception:
                raise SongpalException("Unknown return type: %s" % x) from ex

        return obj

    @staticmethod
    def from_payload(name, inputs, outputs, version):
        ins = None
        outs = None
        if len(inputs) != 0:
            ins = MethodSignature.parse_json_types(inputs.pop())
        if len(outputs) != 0:
            outs = MethodSignature.parse_json_types(outputs.pop())

        return MethodSignature(name=name, input=ins, output=outs, version=version)

    def _serialize_types(self, x):
        """Convert type to string."""
        if x is None:
            return x

        def serialize(x):
            if isinstance(x, str):
                return x
            return x.__name__

        if isinstance(x, dict):
            serialized_dict = {k: serialize(v) for k, v in x.items()}
            return serialized_dict
        serialized = serialize(x)
        return serialized

    def serialize(self):
        return {
            "name": self.name,
            "input": self._serialize_types(self.input),
            "output": self._serialize_types(self.output),
            "version": self.version,
        }

    name = attr.ib()
    input = attr.ib()
    output = attr.ib()
    version = attr.ib()


class Method:
    """A Method (int. API) represents a single API method.

    This class implements __call__() for calling the method, which can be used to
    invoke the method.
    """

    def __init__(self, service, signature: MethodSignature, debug=0):
        """Construct a method."""
        self.versions = signature.version
        self.name = signature.name
        self.service = service

        self.debug = debug
        self.signature = signature

        self.version = self.signature.version

    def asdict(self) -> Dict[str, Union[Dict, Union[str, Dict]]]:
        """Return a dictionary describing the method.

        This can be used to dump the information into a JSON file.
        """
        return {"service": self.service.name, **self.signature.serialize()}

    async def __call__(self, *args, **kwargs):
        """Call the method with given parameters.

        On error this call will raise a :class:SongpalException:. If the error is
        reported by the device (e.g. not a problem doing the request), the exception
        will contain `error` attribute containing the device-reported error message.
        """
        try:
            res = await self.service.call_method(self, *args, **kwargs)
        except Exception as ex:
            raise SongpalException("Unable to make a request: %s" % ex) from ex

        if self.debug > 1:
            _LOGGER.debug("got payload: %s" % res)

        if "error" in res:
            _LOGGER.debug(self)
            raise SongpalException(
                "Got an error for {}: {}".format(self.name, res["error"]),
                error=res["error"],
            )

        if self.debug > 0:
            _LOGGER.debug("got res: %s" % pf(res))

        if "result" not in res:
            _LOGGER.error("No result in response, how to handle? %s" % res)
            return

        res = res["result"]
        if len(res) > 1:
            _LOGGER.warning("Got a response with len >  1: %s" % res)
            return res
        elif len(res) < 1:
            _LOGGER.debug("Got no response, assuming success")
            return True

        return res[0]

    @property
    def inputs(self) -> Dict[str, type]:
        """Input parameters for this method."""
        return self.signature.input

    @property
    def outputs(self) -> Dict[str, type]:
        """Output parameters for this method."""
        return self.signature.output

    def __repr__(self):
        return "<Method {}.{}({}) -> {}>".format(
            self.service.name,
            self.name,
            pf(self.inputs),
            pf(self.outputs),
        )
