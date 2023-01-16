import config
import yfinance
import pandas as pd
import datetime
from requests_html import HTMLSession


def date_string_to_datetime(date_string):
	return datetime.datetime.strptime(date_string, "%Y-%m-%d")


def get_next_day_string(current_day_string):
	current_day_datetime = date_string_to_datetime(current_day_string)
	next_day_datetime = current_day_datetime + datetime.timedelta(days=1)
	next_day_string = next_day_datetime.strftime("%Y-%m-%d")
	return next_day_string


def date_range(start_datetime, end_datetime):
    for i in range(int((end_datetime - start_datetime).days) + 1):
        yield start_datetime + datetime.timedelta(i)


def get_data_for_quote(quote, start_time, end_time):
	df = yfinance.download(quote, start=get_next_day_string(start_time), end=get_next_day_string(end_time), interval="1d", auto_adjust=True, prepost=True, threads=True)
	df = df.reset_index()
	df = df.dropna()
	return df


def is_crypto_undervalued(df):
	moving_average = df.loc[:, "Close"].mean()
	return df["Close"].iloc[-1] < moving_average


def get_total_start_and_end_time(moving_average_size):
	start_time = datetime.datetime.utcnow() + datetime.timedelta(days=-moving_average_size)
	end_time = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
	return start_time.strftime("%Y-%m-%d"), end_time.strftime("%Y-%m-%d")


def get_total_crypto_quotes_list(maximum_cryptos_to_consider):
	html_session = HTMLSession()
	yfinance_response = html_session.get(f"https://finance.yahoo.com/crypto?offset=0&count={maximum_cryptos_to_consider}")
	df = pd.read_html(yfinance_response.html.raw_html)               
	df = df[0].copy()
	total_crypto_quotes_list = df.Symbol.tolist()
	return total_crypto_quotes_list


def get_undervalued_cryptos_list(quote_names_list, start_time, end_time):
	undervalued_cryptos_list = []
	for quote_name in quote_names_list:
		print("Quote:", quote_name)
		df = get_data_for_quote(quote_name, start_time, end_time)
		print("Data downloaded")
		if df.shape[0] == 0:
			continue
		if is_crypto_undervalued(df):
			undervalued_cryptos_list.append(quote_name[:-4])
			print(quote_name[:-4], "is undervalued")
		else:
			print(quote_name[:-4], "is not undervalued")
		print("_" * 80)
	return undervalued_cryptos_list


def run(moving_average_size, maximum_cryptos_to_consider):
	start_time, end_time = get_total_start_and_end_time(moving_average_size)
	crypto_quotes_list = get_total_crypto_quotes_list(maximum_cryptos_to_consider)
	undervalued_cryptos_list = get_undervalued_cryptos_list(crypto_quotes_list, start_time, end_time)
	return undervalued_cryptos_list



def main():
	undervalued_cryptos_list = run(config.MOVING_AVERAGE_SIZE, config.MAXIMUM_CRYPTOS_TO_CONSIDER)
	print("Undervalued cryptos:")
	for crypto_name in undervalued_cryptos_list:
		print(crypto_name)


if __name__ == "__main__":
	main()
