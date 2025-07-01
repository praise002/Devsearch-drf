from rest_framework.response import Response


class CustomResponse:
    @staticmethod
    def success(message, data=None, status_code=200, headers=None):
        response = {
            "status": "success",
            "message": message,
        }
        if data is not None:
            response["data"] = data
        return Response(data=response, status=status_code, headers=headers)

    @staticmethod
    def info(message, data=None, status_code=200, headers=None):
        response = {
            "status": "info",
            "message": message,
        }
        if data is not None:
            response["data"] = data
        return Response(data=response, status=status_code, headers=headers)

    @staticmethod
    def error(message, err_code, data=None, status_code=400, headers=None):
        response = {
            "status": "failure",
            "message": message,
            "code": err_code,
        }

        if data is not None:
            response["data"] = data

        return Response(data=response, status=status_code, headers=headers)
