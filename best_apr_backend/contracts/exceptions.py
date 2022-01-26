class ContractNotFound(Exception):
    pass


class ContractMultipleObjectsReturned(Exception):
    pass


class ContractDoesNotExistsInOtherBlockChain(Exception):
    pass


class ContractPaused(Exception):
    pass


class ContractTransactionAlreadyProcessed(Exception):
    pass


class ContractTransactionAlreadyReverted(Exception):
    pass


class InsufficientTokenBalance(Exception):
    pass


class InsufficientCryptoBalance(Exception):
    pass


class GasPriceExeedsSpeciefedLimitUnderContract(Exception):
    pass


class TokenPriceRateChanged(Exception):
    pass
