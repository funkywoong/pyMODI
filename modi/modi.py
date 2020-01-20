# -*- coding: utf-8 -*-

"""Main module."""

from __future__ import absolute_import

import os
import time
import serial

from modi._processes import SerialProcess, ParsingProcess, ExeThread
from modi._command import Command
from modi.module import (
    button,
    dial,
    display,
    env,
    gyro,
    ir,
    led,
    mic,
    motor,
    network,
    speaker,
    ultrasonic,
)

from multiprocessing import Process, Queue


class MODI:
    """
    :param str port: MODI network module device name or ``None``.

    :raises SerialException: In case the device can not be found or can not be configured.

    The port is immediately opened on object creation, when a *port* is given. It is configured automatically when *port* is ``None`` and a successive call to :meth:`~modi.modi.MODI.open` is required.

    *port* is a device name: depending on operating system. e.g. ``/dev/ttyUSB0`` on GNU/Linux or ``COM3`` on Windows.

    Example:

    >>> import modi
    >>> bundle = modi.MODI()

    It can also be used with :meth:`modi.serial.list_ports`.

    >>> import modi
    >>> import modi.serial
    >>> ports = modi.serial.list_ports() # [<serial.tools.list_ports_common.ListPortInfo object at 0x1026e95c0>]
    >>> bundle = modi.MODI(ports[0].device)
    """

    def __init__(self, port=None):
        print("os.getpid():", os.getpid())

        self._serial_read_q = Queue(100)
        self._serial_write_q = Queue(100)
        self._recv_q = Queue(100)
        self._send_q = Queue(100)
        self._display_send_q = Queue(100)

        self._src_ids = dict()
        self._modules = list()
        self._cmd = Command()

        print("Serial Process Start")
        self._ser_proc = SerialProcess(self._serial_read_q, self._serial_write_q, port)
        self._ser_proc.daemon = True
        self._ser_proc.start()

        print("Parsing Process Start")
        self._par_proc = ParsingProcess(self._serial_read_q, self._recv_q)
        self._par_proc.daemon = True
        self._par_proc.start()

        print("Excute Process Start")
        self._exe_thrd = ExeThread(
            self._serial_write_q, self._recv_q, self._src_ids, self._modules, self._cmd
        )
        self._exe_thrd.daemon = True
        self._exe_thrd.start()

        self._init_modules()

    def _init_modules(self):
        broadcast_id = 0xFFF

        msg_to_send = self._cmd.module_state(
            broadcast_id, self._cmd.ModuleState.REBOOT, self._cmd.ModulePnp.OFF
        )
        self._serial_write_q.put(msg_to_send)
        self.__delay()

        msg_to_send = self._cmd.module_state(
            broadcast_id, self._cmd.ModuleState.RUN, self._cmd.ModulePnp.OFF
        )
        self._serial_write_q.put(msg_to_send)
        self.__delay()

        msg_to_send = self._cmd.request_uuid(broadcast_id)
        self._serial_write_q.put(msg_to_send)
        self.__delay()

    def __delay(self):
        time.sleep(1)

    # def write(self, msg, is_display=False):
    #     """
    #     :param str msg: Data to send.

    #     Put the string to the sending data queue. This should be of type ``str``.
    #     """
    #     if is_display:
    #         self._display_send_q.put(msg)
    #     else:
    #         self._send_q.put(msg)

    def exit(self):
        print("You are now leaving the Python sector.")
        self._ser_proc.stop()
        self._par_proc.stop()
        self._exe_thrd.stop()

    @property
    def modules(self):
        """Tuple of connected modules except network module.

        Example:

        >>> bundle = modi.MODI()
        >>> modules = bundle.modules # (<modi.module.button.Button object at 0x1009455c0>, <modi.module.led.Led object at 0x100945630>)
        """
        return tuple(self._modules)

    @property
    def buttons(self):
        """Tuple of connected :class:`~modi.module.button.Button` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "button"])

    @property
    def dials(self):
        """Tuple of connected :class:`~modi.module.dial.Dial` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "dial"])

    @property
    def displays(self):
        """Tuple of connected :class:`~modi.module.display.Display` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "display"])

    @property
    def envs(self):
        """Tuple of connected :class:`~modi.module.env.Env` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "env"])

    @property
    def gyros(self):
        """Tuple of connected :class:`~modi.module.gyro.Gyro` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "gyro"])

    @property
    def irs(self):
        """Tuple of connected :class:`~modi.module.ir.Ir` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "ir"])

    @property
    def leds(self):
        """Tuple of connected :class:`~modi.module.led.Led` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "led"])

    @property
    def mics(self):
        """Tuple of connected :class:`~modi.module.mic.Mic` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "mic"])

    @property
    def motors(self):
        """Tuple of connected :class:`~modi.module.motor.Motor` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "motor"])

    @property
    def speakers(self):
        """Tuple of connected :class:`~modi.module.speaker.Speaker` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "speaker"])

    @property
    def ultrasonics(self):
        """Tuple of connected :class:`~modi.module.ultrasonic.Ultrasonic` modules.
        """
        return tuple([x for x in self.modules if x.mtype == "ultrasonic"])
