from unittest.mock import NonCallableMock, Mock, patch
from cloudMonitoring.collect_vm_stats import (
    number_servers_active,
    number_servers_build,
    number_servers_error,
    number_servers_shutoff,
    number_servers_total,
    get_all_server_statuses,
    server_obj_to_len,
    main,
)


def test_server_obj_to_len():
    """
    Tests that the length of a generator object is returned
    """
    mock_generator_obj = iter([NonCallableMock(), NonCallableMock(), NonCallableMock()])
    res = server_obj_to_len(mock_generator_obj)
    assert res == 3


def test_number_servers_total():
    """
    Tests that the total number of servers can be queried and counted
    """
    mock_conn = Mock()
    mock_server_results = iter(
        [NonCallableMock(), NonCallableMock(), NonCallableMock()]
    )
    mock_conn.compute.servers.return_value = mock_server_results
    num_returned = number_servers_total(mock_conn)
    assert num_returned == 3


def test_number_servers_active():
    """
    Tests that the active servers can be queried and counted
    """
    mock_conn = Mock()
    mock_server_results = iter(
        [NonCallableMock(), NonCallableMock(), NonCallableMock()]
    )
    mock_conn.compute.servers.return_value = mock_server_results
    num_returned = number_servers_active(mock_conn)
    assert num_returned == 3


def test_number_servers_build():
    """
    Tests that the servers in build state can be queried and counted
    """
    mock_conn = Mock()
    mock_server_results = iter(
        [NonCallableMock(), NonCallableMock(), NonCallableMock()]
    )
    mock_conn.compute.servers.return_value = mock_server_results
    num_returned = number_servers_build(mock_conn)
    assert num_returned == 3


def test_number_servers_error():
    """
    Tests that the error servers can be queried and counted
    """
    mock_conn = Mock()
    mock_server_results = iter(
        [NonCallableMock(), NonCallableMock(), NonCallableMock()]
    )
    mock_conn.compute.servers.return_value = mock_server_results
    num_returned = number_servers_error(mock_conn)
    assert num_returned == 3


def test_number_servers_shutoff():
    """
    Tests that the shutoff servers can be queried and counted
    """
    mock_conn = Mock()
    mock_server_results = iter(
        [NonCallableMock(), NonCallableMock(), NonCallableMock()]
    )
    mock_conn.compute.servers.return_value = mock_server_results
    num_returned = number_servers_shutoff(mock_conn)
    assert num_returned == 3


@patch("cloudMonitoring.collect_vm_stats.connect")
def test_get_all_server_statuses(mock_connect):
    """
    Tests that get_all_server_statuses calls appropriate functions and returns
    data string to send to influx
    """

    def _mock_server_call(num_to_return):
        """stubs out server call
        :param num_to_return: number of mock objects to return
        """
        return iter(NonCallableMock() for _ in range(num_to_return))

    mock_connect.return_value.compute.servers.side_effect = [
        # total number found
        _mock_server_call(10),
        # active number found
        _mock_server_call(4),
        # build number found
        _mock_server_call(3),
        # error number found
        _mock_server_call(2),
        # shutoff number found
        _mock_server_call(1),
    ]

    mock_cloud_name = "prod"
    res = get_all_server_statuses(mock_cloud_name)

    assert res == (
        "VMStats,instance=Prod "
        "totalVM=10i,activeVM=4i,"
        "buildVM=3i,errorVM=2i,shutoffVM=1i"
    )


@patch("cloudMonitoring.collect_vm_stats.run_scrape")
@patch("cloudMonitoring.collect_vm_stats.parse_args")
def test_main(mock_parse_args, mock_run_scrape):
    """
    tests main function calls run_scrape utility function properly
    """
    mock_user_args = NonCallableMock()
    main(mock_user_args)
    mock_run_scrape.assert_called_once_with(
        mock_parse_args.return_value, get_all_server_statuses
    )
    mock_parse_args.assert_called_once_with(
        mock_user_args, description="Get All VM Statuses"
    )
