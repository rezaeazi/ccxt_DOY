const ccxtModule = require('./dist/cjs/ccxt.js');
const ccxt = ccxtModule.default || ccxtModule;

async function main() {
    const exchange = new ccxt.nobitex();
    
    console.log("Exchange ID:", exchange.id);
    console.log("Exchange Name:", exchange.name);
    
    try {
        // تست متد fetchMarkets
        const markets = await exchange.fetchMarkets();
        console.log("Markets count:", markets.length);
        console.log("First market:", markets[0].symbol);

        // تست متد fetchTicker
        const ticker = await exchange.fetchTicker('BTC/IRT'); 
        console.log("BTC/IRT Ticker:", ticker);
    } catch (e) {
        console.log("Error:", e.message);
    }
}

main();