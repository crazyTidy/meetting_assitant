#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def get_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FastApi Swagger UI",
        swagger_js_url="/statics/javascripts/swagger-ui-bundle.js",
        swagger_css_url="/statics/styles/swagger-ui.css",
        swagger_favicon_url="/statics/icons/favicon.png",
    )


def main():
    pass


if __name__ == "__main__":
    main()
