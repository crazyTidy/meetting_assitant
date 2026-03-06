#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """基类，不创建表。"""

    __abstract__ = True

    # 建议用 uuid
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False, comment="主键 id，唯一")
    create_time = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment="更新时间")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="删除标志位")


def main():
    pass


if __name__ == "__main__":
    main()
