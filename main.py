"""
Ping the IP address ranges 192.168.1.0/24 and 192.168.2.0/24 and report all IP addresses that are pingable on one range,
but not on the other. For example, if we find that 192.168.1.34 is pingable, but 192.168.2.34 is not pingable,
then that is a case we want to know about. Similarly, if 192.168.2.34 is pingable, but 192.168.1.34 is not pingable,
we also need to know about that.

• Use python3.6 or higher
• Your code needs to run quickly, so some kind of multi-threading, multi-tasking is necessary
• You will need to retry IP addresses that fail the first ping. The number of retry attempts is
up to you.
• Your code must pass PEP8 and include comments and docstrings where appropriate.
• Include mock-tests, unit-tests, any kind of tests that you write to help prove that your
code behaves as expected.
• For bonus points, allow specific IP addresses to be skipped based on their last octet, so
for example we could exclude 192.168.1.56 and 192.168.2.56 by specifying '56' to
some function in your code.
"""

from concurrent import futures
from datetime import date
import subprocess
import logging
import time
import sys

logging_tool = logging.getLogger()


class Network:
    def __init__(self, network_id, retries, skip_ip=None):
        if skip_ip is None:
            skip_ip = {}
        self.network_id = network_id
        self.skip_ip = skip_ip  # set containing last octet of the ip addresses we want to skip
        self.retries = retries

    def run_ping_sweep(self, no_threads):
        """Create a pool of threads to execute the ping sweep in a concurrent manner.
        Retry pinging the unresponsive addressed for the amount of times given by the
        "retries" attribute.

        Return a list of IPv4 addresses that were unresponsive even after retry.

        Arguments:
            no_threads: the max number of threads to be created by executor
        """
        logging_tool.info(f"Begin pinging network ID: {self.network_id}")
        with futures.ThreadPoolExecutor(no_threads) as executor:
            unresponsive_ips = []
            futures_list = [
                (host, executor.submit(ping, host))
                for host in ("%s.%d" % (self.network_id, i) for i in range(255)
                             if i not in self.skip_ip)
            ]
        for ip, fut in futures_list:
            if not fut.result():
                unresponsive_ips.append(int(ip.split(".")[-1]))
                logging.debug(f"First attempt: {ip} is unresponsive. "
                              f"Adding it to the retry list")
            else:
                logging.info(f"Address {ip} successfully pinged!")

        def retry():
            retries = 0
            while retries < self.retries:
                logging.info(f"Retrial no.{retries + 1}/{self.retries} "
                             f"for network ID: {self.network_id}")
                with futures.ThreadPoolExecutor(no_threads) as retry_executor:
                    futures_retry_list = [
                        (host, retry_executor.submit(ping, host))
                        for host in ("%s.%d" % (self.network_id, i)
                                     for i in unresponsive_ips)
                    ]
                    for retry_ip, retry_fut in futures_retry_list:
                        if retry_fut.result():
                            unresponsive_ips.remove(int(retry_ip.split(".")[-1]))
                            logging.info(f"{retry_ip} successfully pinged. "
                                         f"Removing from retry list!")
                        else:
                            logging.debug(f"Retry no.{retries + 1}/{self.retries}: "
                                          f"{retry_ip} is still unresponsive")
                retries += 1
            return unresponsive_ips

        return retry()


def ping(hostname):
    """Ping an IPv4 address within the "network_id" range and
    return "True" if the ping was successful and "False" otherwise.
    """
    # import pdb; pdb.set_trace()
    p = subprocess.Popen(["ping", "-c", "1", "-W", "1",
                          hostname],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    return p.wait() == 0


def compare_networks_response(n1, n2):
    """Log all IP addresses that are pingable on one range, but not on the other."""
    unresponsive_n1 = n1.run_ping_sweep(255)
    unresponsive_n2 = n2.run_ping_sweep(255)
    n1_exclusively = list(set(unresponsive_n1).difference(unresponsive_n2) - set(n2.skip_ip))
    n1_exclusively.sort()
    n2_exclusively = list(set(unresponsive_n2).difference(unresponsive_n1) - set(n1.skip_ip))
    n2_exclusively.sort()
    logging_tool.info(f"Comparing {n1.network_id} and {n2.network_id}:")
    logging_tool.info(f"Network nodes responsive exclusively on network ID {n2.network_id} "
                      f"(skipped: {n1.skip_ip}): {n1_exclusively}.")
    logging_tool.info(f"Network nodes responsive exclusively on network ID {n1.network_id} "
                      f"(skipped: {n2.skip_ip}): {n2_exclusively}.")
    return n1_exclusively, n2_exclusively


def log_init(log_instance):
    """Sets up logging facilities.

    :return: Logger instance.
    """
    log_instance.setLevel(logging.DEBUG)
    log_time_stamp = time.strftime("%Y-%m-%dT%H%M%S")
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                      datefmt='%H:%M:%S%p')

    file_handler = logging.FileHandler(f"network_pingTest_{log_time_stamp}.log")
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    log_instance.addHandler(file_handler)
    log_instance.addHandler(console_handler)


def main():
    log_init(logging_tool)
    logging_tool.info(f'{date.today().strftime("%d/%m/%Y")} - Start logging')

    res_code = 0

    # TODO: ArgumentParser infrastructure

    t_start = time.perf_counter()

    # n1 = Network("192.168.1", 1, skip_ip={134, 245})
    # n2 = Network("192.168.2", 2)
    # compare_networks_response(n1, n2)

    n3 = Network("8.8.8", 2)#, skip_ip={8})      # Only .8 is pingable
    n4 = Network("44.237.234", 1)#, skip_ip={227, 178})
    # n5 = Network("104.16.51", 1)  # Cloudfare protected network. All addresses are pingable
    # compare_networks_response(n3, n4)
    compare_networks_response(n3, n4)

    t_stop = time.perf_counter()
    logging_tool.info("Ping sweep time (with retries):"
                      " %.3f" % (t_stop - t_start))
    logging_tool.info('Finished logging')

    return res_code


if __name__ == '__main__':
    result_code = -1
    try:
        result_code = main()
    except Exception as e:
        logging_tool.exception(e)
        result_code = -2

    sys.exit(result_code)
