import unittest
import main
from main import Network as Net
from unittest.mock import MagicMock, patch


# TODO: Add mock tests -> subprocess.Popen


def ping_network_pair(nwrk1, nwrk1_retries, nwrk2, nwrk2_retries,
                      skip_ip1=None, skip_ip2=None):
    """Setup for test functions.

    Arguments:
        nwrk1: first network IDs to be pinged (similarly nwrk2)
        nwrk1_retries: the amount of times will ping the
        unresponsive nodes within first network (similarly
        nwrk1_retries)
        skip_ip1: last octet of addresses to be skipped
        (similarly skip_ip2)
    """
    if skip_ip1 is None:
        skip_ip1 = {}
    if skip_ip2 is None:
        skip_ip2 = {}
    n1 = Net(nwrk1, nwrk1_retries, skip_ip=skip_ip1)
    n2 = Net(nwrk2, nwrk2_retries, skip_ip=skip_ip2)
    result = main.compare_networks_response(n1, n2)
    print(f"{n2.network_id} vs {n1.network_id} :")
    print(f"Network nodes responsive exclusively on "
          f"network ID {n2.network_id}: {result[0]}.")
    print(f"Network nodes responsive exclusively on "
          f"network ID {n1.network_id}: {result[1]}.")
    return result


# Unreliable tests scenarios (result dependent on server
# availability and LAN config). Mock testing required.
class TestNetworkPing(unittest.TestCase):

    def test_1(self):
        result = ping_network_pair("192.168.1", 1, "192.168.2", 2)
        expected = ([], [])
        self.assertEqual(expected, result)

    def test_2(self):
        result = ping_network_pair("8.8.8", 2, "44.237.234", 1)
        expected = ([5, 9, 108, 110, 122, 158, 168, 178, 179, 227, 239, 245, 247, 250], [8])
        self.assertEqual(expected, result)

    def test_3(self):
        result = ping_network_pair("44.237.234", 3, "8.8.8", 2)
        expected = ([8], [5, 9, 108, 110, 122, 158, 168, 178, 179, 227, 239, 245, 247, 250])
        self.assertEqual(expected, result)

    # 104.16.51 is a Cloudfare protected network. All addresses should be pingable
    def test_4(self):
        result = ping_network_pair("104.16.51", 3, "44.237.234", 3, None, {45, 200})
        expected = ([], [0, 1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                         19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
                         34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49,
                         50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
                         65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                         80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94,
                         95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
                         109, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,
                         123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134,
                         135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146,
                         147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158,
                         159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170,
                         171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182,
                         183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194,
                         195, 196, 197, 198, 199, 201, 202, 203, 204, 205, 206, 207,
                         208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
                         220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
                         232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243,
                         244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254])
        self.assertEqual(expected, result)

    def test_5(self):
        result = ping_network_pair("8.8.8", 3, "44.237.234", 3, {8}, {227, 178})
        expected = ([5, 9, 108, 110, 122, 158, 168, 179, 239, 245, 247, 250], [])
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
