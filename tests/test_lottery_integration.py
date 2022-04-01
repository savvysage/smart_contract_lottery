from brownie import network
import pytest
import time
from scripts.common import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    initial_lottery_balance = lottery.balance()
    initial_winner_balance = account.balance()
    expected_new_lottery_balance = 0
    expected_new_winner_balance = initial_winner_balance + initial_lottery_balance
    # print(initial_lottery_balance)
    # print(initial_winner_balance)
    # print(expected_new_lottery_balance)
    # print(expected_new_winner_balance)
    # Act
    tx = lottery.endLottery({"from": account})
    time.sleep(180)
    new_lottery_balance = lottery.balance()
    new_winner_balance = account.balance()
    # print(new_lottery_balance)
    # print(new_winner_balance)
    # winner = lottery.recentWinner()
    # print(winner)
    # Assert
    assert lottery.recentWinner() == account
    assert new_lottery_balance == expected_new_lottery_balance
    # assert new_winner_balance == expected_new_winner_balance
