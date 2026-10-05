from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class UiFiles(StaticFiles):
    """Serve the built React app.

    A page address such as /people/7 is not a file. It gets index.html, and the
    app shows the right page once it loads. Unknown API paths stay 404.
    """

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code != 404 or path.startswith("api/"):
                raise
            return await super().get_response("index.html", scope)
