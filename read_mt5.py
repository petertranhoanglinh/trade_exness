import MetaTrader5 as mt5
if not mt5.initialize():
    print("MT5 initialization failed:", mt5.last_error())
    quit()
account_info = mt5.account_info()

symbols = mt5.symbols_get()
print("Danh sách các symbol hiện có:")
for s in symbols:
    print(s.name)

if account_info is None:
    print("Không lấy được thông tin tài khoản:", mt5.last_error())
else:
    for field in dir(account_info):
        if not field.startswith("_"):
            print(f"{field}: {getattr(account_info, field)}")

mt5.shutdown()
