import telnetlib
import pymysql
import time
from config import host, user, password, db_name

# encode strings for telnetlib
def to_bytes(line):
    return f"{line}\n".encode("utf-8")

# input data
ip = input("ip: ")
login = input("login: ")
psw = input("password: ")

id_in_table = int(input("id: "))
ports = int(input("ports: "))

# output data will here
output = open("output.txt", "w")


try:
    # connection to switchboard
    with telnetlib.Telnet(ip) as telnet:
        telnet.read_until(b"Username")
        telnet.write(to_bytes(login))
        telnet.read_until(b"Password")
        telnet.write(to_bytes(password))

        print("Succesfully connected...")
        print("#" * 30)

        try:
            # connection to mysql
            connection = pymysql.connect(
                host = host,
                port = 3306,
                user = user,
                password = password,
                database = db_name,
                cursorclass = pymysql.cursors.DictCursor
            )
            print("Succesfully connected to database...")
            print("#" * 30)
            
            # Executing the commands from database
            try:
                with connection.cursor() as cursor:
                    select_commands = "SELECT command FROM telnet_commands WHERE id=%s;"
                    cursor.execute(select_commands, (id_in_table,))

                    commands = cursor.fetchone()
                    commands = commands.get("command").split("\r\n")

                    for i in range(len(commands)):
                        telnet.write(to_bytes(commands[i].format(ports)))
                        time.sleep(5)
                        output.write(telnet.read_very_eager().decode('utf-8'))

                    print("Succesfully executed. The results were recorded in output.txt")

            # exception handling
            except Exception as ex3:
                print("Executing failed")
                print(ex3)

            finally:
                connection.close()


        except Exception as ex2:
            print("Connection to database refused...")
            print(ex2)
        finally:
            #telnet.close()
            pass

except Exception as ex:
    print("Connection failed...")
    print(ex)
