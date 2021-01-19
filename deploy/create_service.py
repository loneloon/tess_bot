import os

package_path = os.path.abspath("..")

if os.path.exists("/usr/lib/systemd/system"):
    if not os.path.exists("/usr/lib/systemd/system/tess_bot.service"):
        try:
            with open("daemon_template", "r") as f:
                file = f.read()

            file = file.replace("*PATH*", package_path)

            with open("/usr/lib/systemd/system/tess_bot.service", "w+") as ns:
                ns.write(file)

        except Exception as e:
            print(e)
            raise SystemExit

    else:
        print("Tess service already exists!\n"
              "Check its status by typing: sudo systemctl status tess_bot")
else:
    print("Encountered unexpected file structure. Can't place daemon.")

