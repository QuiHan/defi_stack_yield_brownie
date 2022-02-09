from brownie import (
    accounts,
    config,
    network,
    Contract,
    interface,
    MockV3Aggregator,
    MockDAI,
    MockWETH,
    LinkToken,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
}


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config if defined,
    otherwise, it will deploy a mock version of that contract, and return that mock contract

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: the most recently
            deployed version of this contract
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # VRFCoordinatorMock.length
            deploy_mocks()
        contract = contract_type[-1]
        # VRFCoordinatorMock[-1] - most recent deployed contract
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_name, contract_address, contract_type.abi)
    return contract


DECIMALS = 18
INITIAL_VALUE = 2000000000000000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    """
    Use this script if you want to deploy mocks to testnet
    """
    account = get_account()
    print("Deploying mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print("Deploying mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print("Deploying mock DAI...")
    dai_token = MockDAI.deploy({"from": account})
    print("Deploying mock WETH...")
    weth_token = MockWETH.deploy({"from": account})
    print(f"DEPLOYED!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # Interact using Interface in contracts/interfaces file
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund Contract!")
    return tx
