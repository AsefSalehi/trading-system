#!/usr/bin/env python3
"""
Trading System Demo Script
Demonstrates the complete trading functionality with profit/loss tracking
"""

import requests
import json
import time
import random
from typing import Dict, Any

API_BASE = "http://localhost:8000/api/v1"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}


class TradingDemo:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.wallet_id = None
        
    def login(self) -> bool:
        """Login and get access token"""
        print("🔐 Logging in as admin...")
        
        response = self.session.post(
            f"{API_BASE}/auth/login/json",
            json=ADMIN_CREDENTIALS
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def create_wallet(self) -> bool:
        """Create a trading wallet"""
        print("💰 Creating trading wallet...")
        
        response = self.session.post(f"{API_BASE}/trading/wallet/create")
        
        if response.status_code == 200:
            data = response.json()
            self.wallet_id = data["id"]
            print(f"✅ Wallet created! Starting balance: ${data['usd_balance']}")
            return True
        else:
            print(f"❌ Wallet creation failed: {response.text}")
            return False
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        response = self.session.get(f"{API_BASE}/trading/portfolio")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get portfolio: {response.text}")
            return {}
    
    def buy_crypto(self, symbol: str, amount: float) -> Dict[str, Any]:
        """Buy cryptocurrency"""
        print(f"📈 Buying ${amount} worth of {symbol}...")
        
        response = self.session.post(
            f"{API_BASE}/trading/buy",
            json={"symbol": symbol, "amount": amount}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bought {data['quantity']:.6f} {symbol} at ${data['price']:.2f}")
            print(f"   Total cost: ${data['total_amount']:.2f} (fee: ${data['fee']:.2f})")
            return data
        else:
            print(f"❌ Buy failed: {response.text}")
            return {}
    
    def sell_crypto(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """Sell cryptocurrency"""
        print(f"📉 Selling {quantity} {symbol}...")
        
        response = self.session.post(
            f"{API_BASE}/trading/sell",
            json={"symbol": symbol, "amount": quantity}
        )
        
        if response.status_code == 200:
            data = response.json()
            pnl = data.get('realized_pnl', 0)
            pnl_pct = data.get('realized_pnl_percentage', 0)
            
            if pnl > 0:
                print(f"✅ Sold {quantity} {symbol} for ${data['total_amount']:.2f}")
                print(f"   💰 PROFIT: ${pnl:.2f} ({pnl_pct:.2f}%)")
            else:
                print(f"✅ Sold {quantity} {symbol} for ${data['total_amount']:.2f}")
                print(f"   📉 LOSS: ${pnl:.2f} ({pnl_pct:.2f}%)")
            
            return data
        else:
            print(f"❌ Sell failed: {response.text}")
            return {}
    
    def simulate_market(self):
        """Simulate market movement"""
        print("🎲 Simulating market movement...")
        
        response = self.session.post(f"{API_BASE}/trading/simulate-market")
        
        if response.status_code == 200:
            print("✅ Market simulation completed!")
        else:
            print(f"❌ Market simulation failed: {response.text}")
    
    def update_portfolio(self):
        """Update portfolio values"""
        response = self.session.post(f"{API_BASE}/trading/update-portfolio")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Portfolio update failed: {response.text}")
            return {}
    
    def print_portfolio_summary(self, portfolio: Dict[str, Any]):
        """Print detailed portfolio summary"""
        print("\n" + "="*60)
        print("📊 PORTFOLIO SUMMARY")
        print("="*60)
        
        print(f"💰 Total Portfolio Value: ${portfolio.get('total_portfolio_value', 0):.2f}")
        print(f"💵 USD Balance: ${portfolio.get('usd_balance', 0):.2f}")
        print(f"📈 Total P&L: ${portfolio.get('total_pnl', 0):.2f} ({portfolio.get('total_pnl_percentage', 0):.2f}%)")
        print(f"📊 Unrealized P&L: ${portfolio.get('total_unrealized_pnl', 0):.2f}")
        print(f"💸 Realized P&L: ${portfolio.get('total_realized_pnl', 0):.2f}")
        print(f"📉 Max Drawdown: {portfolio.get('max_drawdown', 0):.2f}%")
        print(f"🎯 Win Rate: {portfolio.get('win_rate', 0):.2f}%")
        print(f"📋 Total Trades: {portfolio.get('total_trades', 0)}")
        
        holdings = portfolio.get('holdings', [])
        if holdings:
            print(f"\n🏦 CURRENT HOLDINGS ({len(holdings)}):")
            print("-" * 60)
            for holding in holdings:
                pnl = holding['unrealized_pnl']
                pnl_pct = holding['unrealized_pnl_percentage']
                status = "📈 PROFIT" if pnl > 0 else "📉 LOSS" if pnl < 0 else "➖ BREAK-EVEN"
                
                print(f"{holding['symbol']:>6}: {holding['quantity']:>12.6f} @ ${holding['average_buy_price']:>8.2f}")
                print(f"        Current: ${holding['current_price']:>8.2f} | Value: ${holding['current_value']:>10.2f}")
                print(f"        {status}: ${pnl:>8.2f} ({pnl_pct:>6.2f}%)")
                print()
        
        recent_trades = portfolio.get('recent_transactions', [])
        if recent_trades:
            print(f"📋 RECENT TRANSACTIONS ({len(recent_trades)}):")
            print("-" * 60)
            for tx in recent_trades[:5]:  # Show last 5 transactions
                tx_type = tx['type'].upper()
                symbol = tx.get('symbol', 'USD')
                amount = tx['total_amount']
                pnl = tx.get('realized_pnl', 0)
                
                if tx_type in ['BUY', 'SELL'] and symbol != 'USD':
                    qty = tx.get('quantity', 0)
                    price = tx.get('price', 0)
                    print(f"{tx_type:>4} {qty:>10.6f} {symbol} @ ${price:>8.2f} = ${amount:>10.2f}")
                    if pnl != 0:
                        print(f"     P&L: ${pnl:>8.2f}")
                else:
                    print(f"{tx_type:>4} ${amount:>10.2f}")
                print()
        
        print("="*60)
    
    def run_demo(self):
        """Run the complete trading demo"""
        print("🚀 Starting Trading System Demo")
        print("="*50)
        
        # Login
        if not self.login():
            return
        
        # Create wallet
        if not self.create_wallet():
            return
        
        # Show initial portfolio
        portfolio = self.get_portfolio()
        self.print_portfolio_summary(portfolio)
        
        # Demo trading sequence
        cryptos_to_trade = ['BTC', 'ETH', 'ADA', 'SOL', 'DOGE']
        
        print(f"\n🎯 Starting demo trading with {len(cryptos_to_trade)} cryptocurrencies...")
        
        # Phase 1: Buy some cryptocurrencies
        print("\n📈 PHASE 1: BUYING CRYPTOCURRENCIES")
        print("-" * 40)
        
        for crypto in cryptos_to_trade:
            amount = random.uniform(500, 1500)  # Random amount between $500-$1500
            self.buy_crypto(crypto, amount)
            time.sleep(1)  # Small delay
        
        # Update and show portfolio
        self.update_portfolio()
        portfolio = self.get_portfolio()
        self.print_portfolio_summary(portfolio)
        
        # Phase 2: Simulate market movements
        print("\n🎲 PHASE 2: MARKET SIMULATION")
        print("-" * 40)
        
        for i in range(3):
            print(f"\n🔄 Market Movement #{i+1}")
            self.simulate_market()
            self.update_portfolio()
            
            portfolio = self.get_portfolio()
            total_pnl = portfolio.get('total_pnl', 0)
            pnl_pct = portfolio.get('total_pnl_percentage', 0)
            
            if total_pnl > 0:
                print(f"📈 Portfolio up ${total_pnl:.2f} ({pnl_pct:.2f}%)")
            else:
                print(f"📉 Portfolio down ${total_pnl:.2f} ({pnl_pct:.2f}%)")
            
            time.sleep(2)
        
        # Phase 3: Sell some positions
        print("\n📉 PHASE 3: TAKING PROFITS/LOSSES")
        print("-" * 40)
        
        portfolio = self.get_portfolio()
        holdings = portfolio.get('holdings', [])
        
        # Sell half of each holding
        for holding in holdings:
            if holding['quantity'] > 0:
                sell_quantity = holding['quantity'] * 0.5  # Sell 50%
                self.sell_crypto(holding['symbol'], sell_quantity)
                time.sleep(1)
        
        # Final portfolio summary
        print("\n🏁 FINAL RESULTS")
        print("-" * 40)
        
        self.update_portfolio()
        final_portfolio = self.get_portfolio()
        self.print_portfolio_summary(final_portfolio)
        
        # Summary statistics
        final_value = final_portfolio.get('total_portfolio_value', 10000)
        initial_value = 10000
        total_return = final_value - initial_value
        total_return_pct = (total_return / initial_value) * 100
        
        print(f"\n🎯 TRADING SESSION SUMMARY:")
        print(f"   Initial Balance: ${initial_value:,.2f}")
        print(f"   Final Balance: ${final_value:,.2f}")
        print(f"   Total Return: ${total_return:,.2f} ({total_return_pct:.2f}%)")
        
        if total_return > 0:
            print(f"   🎉 PROFITABLE SESSION! You made ${total_return:.2f}!")
        elif total_return < 0:
            print(f"   😔 LOSING SESSION. You lost ${abs(total_return):.2f}")
        else:
            print(f"   😐 BREAK-EVEN SESSION")
        
        print(f"   📊 Total Trades: {final_portfolio.get('total_trades', 0)}")
        print(f"   🎯 Win Rate: {final_portfolio.get('win_rate', 0):.1f}%")
        print(f"   📉 Max Drawdown: {final_portfolio.get('max_drawdown', 0):.2f}%")


def main():
    """Main function"""
    print("🏦 Trading System Demo")
    print("Make sure the trading system is running with: ./start_trading_system.sh")
    print()
    
    # Check if API is accessible
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Trading system is not accessible. Please start it first.")
            return
    except requests.exceptions.RequestException:
        print("❌ Trading system is not running. Please start it with: ./start_trading_system.sh")
        return
    
    demo = TradingDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()