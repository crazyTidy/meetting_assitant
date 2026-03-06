#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging
import traceback
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..settings import environment_config

# 创建引擎和会话
engine = create_engine(environment_config.SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_database_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logging.error(traceback.format_exc())
        session.rollback()
    finally:
        session.close()


def main():
    pass


if __name__ == "__main__":
    main()
