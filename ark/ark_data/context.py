class Context:
    http_client = None
    base_url = None

    @classmethod
    def from_context(cls, ctx):
        instance = cls()
        instance.http_client = ctx.http_client
        instance.base_url = ctx.base_url
        return instance
