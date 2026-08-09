import ccxt from './js/src/ccxt.js';

async function main() {
    const exchange = new ccxt.nobitex({
        apiKey: 'YOUR_TOKEN', // در اینجا توکن خود را وارد کنید
        enableRateLimit: true,
    });

    await exchange.loadMarkets();
    console.log('Exchange:', exchange.id);
    console.log('Markets count:', Object.keys(exchange.markets).length);

    const symbols = Object.keys(exchange.markets)
        .filter(s => s.includes('/USDT'))
        .slice(0, 20);

    console.log('USDT symbols sample:');
    console.dir(symbols, { depth: null });
}

main();