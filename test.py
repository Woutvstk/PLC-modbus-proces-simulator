import snap7
# debug prog voor werking S7
ip = "192.168.111.80"
rack = 0
slot = 1

client = snap7.client.Client()
try:
    client.connect(ip, rack, slot, 102)
    if client.get_connected():
        print(" Verbonden met PLC")
    else:
        print(" Geen verbinding")
except Exception as e:
    print("Fout:", e)
finally:
    client.disconnect()
