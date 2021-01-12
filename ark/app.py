import os
import csv
from datetime import datetime
from pymongo import MongoClient
from .gmail.gmail_service import GmailService
from .ark_data.service import ArkDataService

# fmt: off
ticker_mapping = {
    "3402"      : "TRYIF",
    "3690"      : "MPNGF",
    "4477"      : "BAINF",
    "4689"      : "YAHOF",
    "ARCT UQ"   : "ARCT",
    "MDT UN"    : "MDT",
    "MOG/A"     : "MOG.A",
    "TAK UN"    : "TAK",
    "TREE UW"   : "TREE",
    "URGN UQ"   : "URGN",
    "XRX UN"    : "XRX",
}
# fmt: on

trade_log_root = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "trade_log")

client = MongoClient()
db = client.capiDB


def run():
    user_id = "me"
    query = "ark"
    subject = "ARK Investment Management Trading Information"
    if not check_unread_emails(user_id, query, subject):
        return

    download_ark_trade_logs()
    update_ark_data()


def check_unread_emails(user_id, query, subject):
    gm = GmailService()
    gm_service = gm.get_serivce()

    msg_ids = gm.search_message(gm_service, user_id, query)
    res = [
        [
            gm.mark_read(gm_service, user_id, id)
            for msg in gm.get_message(gm_service, user_id, id)["payload"]["headers"]
            if msg["name"] == "Subject" and subject.lower() in msg["value"].lower()
        ]
        for id in msg_ids
    ]
    return len(res) > 0


def download_ark_trade_logs():
    ark_data = ArkDataService(root_dir=trade_log_root)
    ark_data.download_logs()


def get_child_path(dir):
    return [os.path.join(dir, file) for file in os.listdir(dir)]


def read_latest_trade_logs():
    log_dirs = get_child_path(trade_log_root)
    log_paths = get_child_path(log_dirs[-1])

    for log in log_paths:
        with open(log) as csv_file:
            reader = csv.DictReader(csv_file)
            return [
                {
                    "date": datetime.strptime(row["date"], "%m/%d/%Y"),
                    "fund": row["fund"],
                    "company": row["company"],
                    "ticker": row["ticker"].strip(),
                    "cusip": row["cusip"],
                    "shares": float(row["shares"]),
                    "value": float(row["market value($)"]),
                    "weight": float(row["weight(%)"]),
                }
                for row in reader
                if row["ticker"]
            ]


def update_ark_data():
    new_trades = []
    log_dicts = read_latest_trade_logs()
    for new in log_dicts:
        new["ticker"] = ticker_mapping[new["ticker"]] if new["ticker"] in ticker_mapping else new["ticker"]
        pre = db.ark.holdings.find_one_and_update(
            {"fund": new["fund"], "ticker": new["ticker"]},
            {"$set": new},
            upsert=True,
        )

        if pre is None:
            action = "buy"
            volume = new["shares"]
        elif new["shares"] == pre["shares"]:
            continue
        elif new["shares"] > pre["shares"]:
            action = "buy"
            volume = new["shares"] - pre["shares"]
        else:
            action = "sell"
            volume = pre["shares"] - new["shares"]

        trade = {
            "date": new["date"],
            "action": action,
            "fund": new["fund"],
            "company": new["company"],
            "ticker": new["ticker"],
            "volume": volume,
            "price": new["value"] / new["shares"],
        }
        new_trades.append(trade)

    if len(new_trades) > 0:
        db.ark.trade.insert_many(new_trades)