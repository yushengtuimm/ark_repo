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


def get_log_data(log):
    with open(log) as csv_file:
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
            for row in csv.DictReader(csv_file)
            if row["ticker"]
        ]


def update_ark_data():
    new_trades = []
    log_dir = get_child_path(trade_log_root)[-1]
    for log in get_child_path(log_dir):
        for item in get_log_data(log):
            item["ticker"] = ticker_mapping[item["ticker"]] if item["ticker"] in ticker_mapping else item["ticker"]
            pre = db.ark.holdings.find_one_and_update(
                {"fund": item["fund"], "ticker": item["ticker"]},
                {"$set": item},
                upsert=True,
            )

            if pre is None:
                action = "buy"
                volume = item["shares"]
            elif item["shares"] == pre["shares"]:
                continue
            elif item["shares"] > pre["shares"]:
                action = "buy"
                volume = item["shares"] - pre["shares"]
            else:
                action = "sell"
                volume = pre["shares"] - item["shares"]

            trade = {
                "date": item["date"],
                "action": action,
                "fund": item["fund"],
                "company": item["company"],
                "ticker": item["ticker"],
                "volume": volume,
                "price": item["value"] / item["shares"],
            }
            new_trades.append(trade)

    if len(new_trades) > 0:
        db.ark.trades.insert_many(new_trades)


def full_update():
    db.ark.holdings.drop()
    db.ark.trades.drop()

    log_dirs = get_child_path(trade_log_root)
    new_trades = []
    for i, dir in enumerate(log_dirs):
        if i == 0:
            data = []
            for log in get_child_path(dir):
                for item in get_log_data(log):
                    item["ticker"] = (
                        ticker_mapping[item["ticker"]] if item["ticker"] in ticker_mapping else item["ticker"]
                    )
                    data.append(item)
            db.ark.holdings.insert_many(data)
        else:
            for log in get_child_path(dir):
                for item in get_log_data(log):
                    item["ticker"] = (
                        ticker_mapping[item["ticker"]] if item["ticker"] in ticker_mapping else item["ticker"]
                    )

                    pre = db.ark.holdings.find_one_and_update(
                        {"fund": item["fund"], "ticker": item["ticker"]},
                        {"$set": item},
                        upsert=True,
                    )

                    if pre is None:
                        action = "buy"
                        volume = item["shares"]
                    elif item["shares"] == pre["shares"]:
                        continue
                    elif item["shares"] > pre["shares"]:
                        action = "buy"
                        volume = item["shares"] - pre["shares"]
                    else:
                        action = "sell"
                        volume = pre["shares"] - item["shares"]

                    trade = {
                        "date": item["date"],
                        "action": action,
                        "fund": item["fund"],
                        "company": item["company"],
                        "ticker": item["ticker"],
                        "volume": volume,
                        "price": item["value"] / item["shares"],
                    }
                    new_trades.append(trade)

    if len(new_trades) > 0:
        db.ark.trades.insert_many(new_trades)
