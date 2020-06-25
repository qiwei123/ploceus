# -*- coding: utf-8 -*-

class PloceusError(Exception): pass

class ArgumentError(PloceusError): pass

class NoGroupFoundError(PloceusError): pass

class RemoteCommandError(PloceusError): pass

class LocalCommandError(PloceusError): pass
