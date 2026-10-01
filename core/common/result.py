from core.common.timestamp import (
    get_timestamp,
)

from core.common.status import (
    Status,
)


class Result:

    @staticmethod
    def success(

        data=None,
        warnings=None,

    ):

        return {

            "success": True,

            "status": Status.SUCCESS,

            "generated_at":

                get_timestamp(),

            "warnings":

                warnings or [],

            "errors": [],

            "data":

                data,

        }

    @staticmethod
    def warning(

        data=None,
        warnings=None,

    ):

        return {

            "success": True,

            "status": Status.WARNING,

            "generated_at":

                get_timestamp(),

            "warnings":

                warnings or [],

            "errors": [],

            "data":

                data,

        }

    @staticmethod
    def error(

        message,

    ):

        return {

            "success": False,

            "status": Status.ERROR,

            "generated_at":

                get_timestamp(),

            "warnings": [],

            "errors": [

                message

            ],

            "data": None,

        }