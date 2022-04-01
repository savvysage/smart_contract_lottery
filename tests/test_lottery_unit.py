from brownie import Lottery, accounts, network, config, exceptions
import pytest
from scripts.common import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert entrance_fee == expected_entrance_fee


def test_cant_enter_lottery_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    # Act
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]
    rand_num = 777
    initial_lottery_balance = lottery.balance()
    initial_winner_balance = get_account(index=(rand_num % 3)).balance()
    expected_new_lottery_balance = 0
    expected_new_winner_balance = initial_winner_balance + initial_lottery_balance
    # print(initial_lottery_balance)
    # print(initial_winner_balance)
    # print(expected_new_lottery_balance)
    # print(expected_new_winner_balance)
    # Act
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, rand_num, lottery.address, {"from": account}
    )
    new_lottery_balance = lottery.balance()
    new_winner_balance = get_account(index=(rand_num % 3)).balance()
    # print(new_lottery_balance)
    # print(new_winner_balance)
    # winner = lottery.recentWinner()
    # print(winner)
    # Assert
    assert lottery.recentWinner() == get_account(index=(777 % 3))
    assert new_lottery_balance == expected_new_lottery_balance
    assert new_winner_balance == expected_new_winner_balance
