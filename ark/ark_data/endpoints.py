from .mixin import Mixin


__all__ = "ArkkEndpoint", "ArkqEndpoint", "ArkwEndpoint", "ArkgEndpoint", "ArkfEndpoint", "PrntEndpoint", "IzrlEndpoint"


class ArkkEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class ArkqEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class ArkwEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class ArkgEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class ArkfEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class PrntEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)


class IzrlEndpoint(Mixin):
    def __init__(self, ctx, filename=None):
        self.ctx = ctx
        self.filename = filename or "ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL_HOLDINGS.csv"

    def execute(self):
        return self.ctx.http_client.get_content("/" + self.filename)