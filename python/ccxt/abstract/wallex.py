from ccxt.base.types import Entry


class ImplicitAPI:
    public_get_v1_markets = publicGetV1Markets = Entry('v1/markets', 'public', 'GET', {})
    public_get_v2_trades_symbol = publicGetV2TradesSymbol = Entry('v2/trades/{symbol}', 'public', 'GET', {})
    private_get_v1_account_balances = privateGetV1AccountBalances = Entry('v1/account/balances', 'private', 'GET', {})
    private_get_v1_account_openorders = privateGetV1AccountOpenOrders = Entry('v1/account/openOrders', 'private', 'GET', {})
    private_post_v1_account_orders = privatePostV1AccountOrders = Entry('v1/account/orders', 'private', 'POST', {})
    private_delete_v1_account_orders = privateDeleteV1AccountOrders = Entry('v1/account/orders', 'private', 'DELETE', {})
