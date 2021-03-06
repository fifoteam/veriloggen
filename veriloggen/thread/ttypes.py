from __future__ import absolute_import
from __future__ import print_function

import veriloggen.types.ram as ram
import veriloggen.types.axi as axi


class RAM(ram.SyncRAMManager):
    __intrinsics__ = ('read', 'write', 'dma_read', 'dma_write')

    def __init__(self, m, name, clk, rst,
                 datawidth=32, addrwidth=10, numports=1, axi=None):

        ram.SyncRAMManager.__init__(
            self, m, name, clk, rst, datawidth, addrwidth, numports)

        self.axi = axi

    def read(self, fsm, addr, port=0, unified=False):
        """ intrinsic read operation """

        if unified:
            return self._unified_read(fsm, addr, port)

        return self._shared_read(fsm, addr, port)

    def write(self, fsm, addr, wdata, port=0, unified=False):
        """ intrinsic write operation """

        if unified:
            return self._unified_write(fsm, addr, wdata, port)

        return self._shared_write(fsm, addr, wdata, port)

    def _shared_read(self, fsm, addr, port=0):
        """ intrinsic read operation using a shared Seq object """

        cond = fsm.state == fsm.current

        rdata, rvalid = ram.SyncRAMManager.read(self, port, addr, cond)
        rdata_reg = self.m.TmpReg(self.datawidth, initval=0)

        fsm.If(rvalid)(
            rdata_reg(rdata)
        )
        fsm.Then().goto_next()

        return rdata_reg

    def _shared_write(self, fsm, addr, wdata, port=0):
        """ intrinsic write operation using a shared Seq object """

        cond = fsm.state == fsm.current

        ram.SyncRAMManager.write(self, port, addr, wdata, cond)
        fsm.goto_next()

        return 0

    def _unified_read(self, fsm, addr, port=0):
        """ intrinsic read operation using the given FSM object """

        fsm(
            self.interfaces[port].addr(addr)
        )

        for _ in range(2):
            fsm.goto_next()

        rdata = self.m.TmpReg(self.datawidth, initval=0)

        fsm(
            rdata(self.interfaces[port].rdata)
        )
        fsm.goto_next()

        return rdata

    def _unified_write(self, fsm, addr, wdata, port=0):
        """ intrinsic write operation using the given FSM object """

        if self._write_disabled[port]:
            raise TypeError('Write disabled.')

        fsm(
            self.interfaces[port].addr(addr),
            self.interfaces[port].wdata(wdata),
            self.interfaces[port].wenable(1)
        )
        fsm.Delay(1)(
            self.interfaces[port].wenable(0)
        )
        fsm.goto_next()

        return 0

#    def dma_read(self, fsm, local_addr, global_addr, size, port=0, nonblocking=False):
#        if self.axi is None or not isinstance(self.axi, AXIM):
#            raise TypeError('AXIM interface is required')
#
#        cond = fsm.state == fsm.current
#
#        done = self.axi.dma_read(self, global_addr, local_addr, size, port)
#
#        if nonblocking:
#            fsm.goto_next()
#            return done
#
#        fsm.If(done).goto_next()
#        return 0
#
#    def dma_write(self, fsm, local_addr, global_addr, size, port=0, nonblocking=False):
#        if self.axi is None or not isinstance(self.axi, AXIM):
#            raise TypeError('AXIM interface is required')
#
#        cond = fsm.state == fsm.current
#
#        done = self.axi.dma_write(self, global_addr, local_addr, size, cond, port)
#
#        if nonblocking:
#            fsm.goto_next()
#            return done
#
#        fsm.If(done).goto_next()
#        return 0


class AXIM(axi.AxiMaster):
    __intrinsics__ = ('write_request', 'write_data',
                      'read_request', 'read_data')

    def __init__(self, m, name, clk, rst, datawidth=32, addrwidth=10):
        axi.AxiMaster.__init__(self, m, name, clk, rst, datawidth, addrwidth)


class AXIS(axi.AxiSlave):

    def __init__(self, m, name, clk, rst, datawidth=32, addrwidth=10):
        axi.AxiSlave.__init__(self, m, name, clk, rst, datawidth, addrwidth)
