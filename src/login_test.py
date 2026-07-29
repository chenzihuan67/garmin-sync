from garminconnect import Garmin

email = input("Garmin 邮箱: ")
password = input("Garmin 密码: ")

client = Garmin(email, password)
client.login()

print("登录成功！")

methods = [m for m in dir(client) if m.startswith("get_")]
for m in sorted(methods):
    print(m)