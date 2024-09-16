import unittest
from unittest.mock import MagicMock, patch
import json
import datetime as dt
from bot.bot import Bot  # assuming Bot is in the 'bot' module

class TestBot(unittest.TestCase):

    def setUp(self):
        # This method will run before every test case
        self.bot = Bot()  # Initialize the bot

    def tearDown(self):
        # Clean up after each test
        self.bot.stop()

    @patch("builtins.open", new_callable=unittest.mock.mock_open, read_data='{"risk_management": {"max_trade_percentage": 0.01}, "error_handling": {}, "logging": {}, "trade_management": {}, "signal_management": {}, "tradable_symbols": {"EURUSD": [{"granularity": "M5", "indicators": {}}]}}')
    def test_load_settings(self, mock_file):
        # Call the load_settings method
        self.bot.load_settings()
        
        # Assert that the risk management settings are correctly loaded
        self.assertEqual(self.bot.risk_management.max_trade_percentage, 0.01)
        
        # Assert that trading symbols are correctly loaded
        self.assertIn("XAUUSD", self.bot.trading_symbols)


    def test_get_next_interval(self):
        # Set up some fake trading times
        self.bot.trading_times = {5, 15, 30}

        # Mock the current time
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = dt.datetime(2024, 9, 16, 14, 27)

            # Call get_next_interval
            next_interval = self.bot.get_next_interval()

            # Expected next interval should be 14:30, because the closest 5-minute interval after 14:27 is 14:30
            expected_interval = dt.datetime(2024, 9, 16, 14, 30)
            self.assertEqual(next_interval, expected_interval)

    @patch("bot.strategy_manager.StrategyManager.generate_signal")
    def test_process_candles(self, mock_generate_signal):
        # Mock generate_signal to return a SignalDecision object
        mock_generate_signal.return_value = "mock_signal"

        # Set up trading symbols with a mock StrategyManager
        mock_strategy_manager = MagicMock()
        self.bot.trading_symbols = {"EURUSD": [mock_strategy_manager]}

        # Call process_candles with triggered symbols
        self.bot.process_candles(["EURUSD"])

        # Assert that the generate_signal method was called
        mock_strategy_manager.generate_signal.assert_called_once()

        # Assert that a signal was added to the current_signals queue
        self.assertEqual(self.bot.current_signals.qsize(), 1)
        self.assertEqual(self.bot.current_signals.get(), "mock_signal")


    # @patch('api.metatrader_api.MT5')
    # def test_mt5_interaction(self, mock_mt5):
    #     # Mock MT5 API interaction
    #     mock_mt5_instance = mock_mt5.return_value
    #     mock_mt5_instance.query_historic_data.return_value = [[(dt.datetime.now(), 1.0, 1.2, 1.1, 1.15, 100)]]
        
    #     # Test candle fetching
    #     self.bot.candle_manager.mt5 = mock_mt5_instance
    #     triggered = self.bot.candle_manager.update_timings()
    #     self.assertIsNotNone(triggered)

if __name__ == '__main__':
    unittest.main()
