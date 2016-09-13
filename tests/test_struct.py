"""Automate struct tests."""
import logging
import unittest
from tests.raw_dump import RawDump

log = logging.getLogger()
RAW_DUMP_ERR = '\n>>>> Raw dump file for this test need to be generated <<<<\n'


class TestStruct(unittest.TestCase):
    """Run tests related to struct packing and unpacking.

    Test the lib with raw dump files from an OpenFlow switch. We assume the
    raw files are valid according to the OF specs to check whether our pack and
    unpack implementations are correct.

    Also, check the minimum size of the struct by instantiating an object with
    no parameters.

    To run these tests, just extends this class and call 2 methods in the
    ``setUp`` method like the example.

    Example:
        .. code-block:: python3

            class MyTest(TestDump):
                @classmethod
                def setUpClass(cls):
                    super().setUpClass()
                    super().set_raw_dump_file('v0x01', 'ofpt_barrier_reply')
                    # Create BarrierReply(xid=5) when needed
                    super().set_raw_dump_object(BarrierReply, xid=5)
                    # As in spec: ``FP_ASSERT(sizeof(struct ...) == ...);``
                    super().set_minimum_size(8)
    """

    def __init__(self, *args, **kwargs):
        """The constructor will avoid that this class tests are executed.

        The tests in this class are executed through the child, so there's no
        no need for them to be executed once more through the parent.
        """
        super().__init__(*args, **kwargs)
        # Override the run method, so it does nothing instead of running the
        # tests (again).
        if self.__class__ == TestStruct:
            self.run = lambda self, *args, **kwargs: None

    _new_raw_dump = None
    _new_raw_object = None
    _msg_cls = None
    _min_size = None

    @classmethod
    def set_raw_dump_file(cls, version, basename):
        """Set which raw dump the tests will use.

        Args:
            protocol_version (str): OpenFlow protocol version,
                e.g. ``v0x01``.
            basename (str): The raw filename without extension.
                E.g. ``ofpt_echo_reply``.
        """
        cls._new_raw_dump = lambda: RawDump(version, basename)

    @classmethod
    def get_raw_dump(cls):
        """Return a new instance of :class:`.RawDump`.

        Use the parameters set in :meth:`set_raw_dump_file`.

        Returns:
            RawDump: with parameters previously set using
                :meth:`set_raw_dump_file`.
        """
        return cls._new_raw_dump()

    @classmethod
    def set_raw_dump_object(cls, msg_cls, *args, **kwargs):
        """Set how to create the object that is dumped in a raw file.

        Args:
            msg_class (:obj:`type`): The message class that is packed as a
                raw file, followed by its parameters to instantiate an
                object.

        Example:
            ``super().__init__(BarrierReply, xid=5)`` will create
            ``BarrierReply(xid=5)``.
        """
        TestStruct._msg_cls = msg_cls
        cls._new_raw_object = lambda: msg_cls(*args, **kwargs)

    @classmethod
    def get_raw_object(cls):
        """Create a new object of the dumped message.

        Use the class and parameters set in :meth:`set_raw_dump_object`.

        Returns:
            A new object using class and parameters priviously set through
                :meth:`set_raw_dump_object`.
        """
        return cls._new_raw_object()

    @classmethod
    def set_minimum_size(cls, size):
        """Set the struct minimum size.

        The minimum size can be found in OF spec. For example,
        :class:`.PhyPort` minimum size is 48 because of
        ``FP_ASSERT(sizeof(struct ofp_phy_port) == 48);`` (spec 1.0.0).

        Args:
            size (int): The minimum size of the struct, in bytes.
        """
        cls._min_size = size

    def test_pack(self):
        """Check whether packed objects equals to dump file."""
        try:
            raw_file = self.get_raw_dump().read()
            msg = self.get_raw_object()
            packed_obj = msg.pack()
            self.assertEqual(packed_obj, raw_file)
        except FileNotFoundError:
            log.warning(RAW_DUMP_ERR)
            raise self.skipTest('There is no raw dump file for this test')
        except:
            self.fail()

    def test_unpack(self):
        """Check whether the unpacked dump equals to expected object."""
        try:
            obj = self.get_raw_object()
            unpacked = self.get_raw_dump().unpack()
            self.assertEqual(unpacked, obj)
        except FileNotFoundError:
            log.error(RAW_DUMP_ERR)
            raise self.skipTest('There is no raw dump file for this test')

    def test_minimum_size(self):
        """Test struct minimum size."""
        if self._min_size is None:
            raise self.skipTest('minimum size not set.')
        try:
            obj = TestStruct._msg_cls()
            self.assertEqual(obj.get_size(), self._min_size)
        except:
            raise self.skipTest('There is no raw dump file for this test')