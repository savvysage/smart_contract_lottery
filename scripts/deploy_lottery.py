from brownie import Lottery, accounts, network, config
from scripts.common import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["key_hash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery.")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_lottery_txn = lottery.startLottery({"from": account})
    start_lottery_txn.wait(1)
    print("Lottery is open!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10 ** 15
    enter_lottery_txn = lottery.enter({"from": account, "value": value})
    enter_lottery_txn.wait(1)
    print("You've entered the lottery.")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    end_lottery_txn = lottery.endLottery({"from": account})
    end_lottery_txn.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner.")
    print("Lottery closed!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
