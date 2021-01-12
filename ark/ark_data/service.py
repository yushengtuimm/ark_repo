import os
from datetime import date

from .context import Context
from .http_client import HttpClient
from .endpoints import ArkkEndpoint, ArkqEndpoint, ArkwEndpoint, ArkgEndpoint, ArkfEndpoint, PrntEndpoint, IzrlEndpoint

dirname = os.path.dirname(__file__)


class ArkDataService:
    def __init__(self, root_dir=None, http_client=None, ark_url=None):
        self.ctx = Context()
        self.root_dir = root_dir or os.path.join(dirname, "trade_log")
        self.ctx.base_url = ark_url or "https://ark-funds.com/wp-content/fundsiteliterature/csv/"
        self.ctx.http_client = http_client or HttpClient(self.ctx.base_url)

    def download_logs(self):
        dir = os.path.join(self.root_dir, str(date.today()))
        if not os.path.exists(dir):
            os.makedirs(dir)
        ctx = Context.from_context(self.ctx)
        ArkkEndpoint(ctx).download_csv(dir)
        ArkqEndpoint(ctx).download_csv(dir)
        ArkwEndpoint(ctx).download_csv(dir)
        ArkgEndpoint(ctx).download_csv(dir)
        ArkfEndpoint(ctx).download_csv(dir)
        PrntEndpoint(ctx).download_csv(dir)
        IzrlEndpoint(ctx).download_csv(dir)