from ccxt.base.types import Entry


class ImplicitAPI:
    public_get_v2_trades_symbol = publicGetV2TradesSymbol = Entry('v2/trades/{symbol}', 'public', 'GET', {})
    public_get_v3_orderbook_symbol = publicGetV3OrderbookSymbol = Entry('v3/orderbook/{symbol}', 'public', 'GET', {})
    public_get_market_stats = publicGetMarketStats = Entry('market/stats', 'public', 'GET', {})
    public_get_status = publicGetStatus = Entry('status', 'public', 'GET', {})
    private_get_users_profile = privateGetUsersProfile = Entry('users/profile', 'private', 'GET', {})
    private_get_users_transactions_history = privateGetUsersTransactionsHistory = Entry('users/transactions-history', 'private', 'GET', {})
    private_get_users_markets_favorite = privateGetUsersMarketsFavorite = Entry('users/markets/favorite', 'private', 'GET', {})
    private_post_users_wallets_list = privatePostUsersWalletsList = Entry('users/wallets/list', 'private', 'POST', {})
    private_post_market_orders_add = privatePostMarketOrdersAdd = Entry('market/orders/add', 'private', 'POST', {})
    private_post_market_orders_cancel = privatePostMarketOrdersCancel = Entry('market/orders/cancel', 'private', 'POST', {})
    private_post_market_orders_list = privatePostMarketOrdersList = Entry('market/orders/list', 'private', 'POST', {})
    private_post_market_orders_update_status = privatePostMarketOrdersUpdateStatus = Entry('market/orders/update-status', 'private', 'POST', {})
    private_post_users_accounts_add = privatePostUsersAccountsAdd = Entry('users/accounts-add', 'private', 'POST', {})
