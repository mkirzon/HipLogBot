import sys
from dotenv import load_dotenv


sys.path.append(
    "/Users/mkirzon/Documents/2023/230901 - Hip Log Bot/hip-log-bot-cloud-function/src"
)


# TRIGGERING FROM CLI, but depends on CWD -
# DOESNT work
# load_dotenv(".env")

# DOESNT WORK
# def pytest_configure():
#     print("running pytest_configure()")
#     # Load the .env file. Assuming it's in the root directory of your project.
#     load_dotenv(".env")

# DOES work
# load_dotenv("hip-log-bot-cloud-function/.env")


# DOES WORK
# def pytest_configure():
#     print("running pytest_configure()")
#     # Load the .env file. Assuming it's in the root directory of your project.
#     load_dotenv("hip-log-bot-cloud-function/.env")
