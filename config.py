# -*- coding: UTF-8 -*-
"""File with all configurations for Task Tree project"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Default config for Task Tree app.

    :param TOKEN_PERIOD: Period of time in seconds for token validity
    :param SECRET_KEY: Maximum secret string
    :param SQLALCHEMY_DATABASE_URI: URI for database
    """
    TOKEN_PERIOD: int = 12*31*24*60*60
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or "____CHANGE___THI$___53CЯET_____"
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///sqlite.db'


@dataclass
class ProductionConfig(Config):
    """Production config for Task Tree app"""
    TOKEN_PERIOD: int = 3*31*24*60*60
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


@dataclass
class DevelopmentConfig(Config):
    """Development config for Task Tree app"""
    SQLALCHEMY_ECHO: bool = True
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = True
