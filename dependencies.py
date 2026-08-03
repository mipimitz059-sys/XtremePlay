from app_config import load_config
from adapters import ConvexAdapter, HerculesAuthAdapter, RealtimeTransportAdapter, WalletProviderAdapter


class Container:
    def __init__(self):
        self.config = load_config()
        self.convex = ConvexAdapter(url=self.config.convex_url)
        self.hercules = HerculesAuthAdapter(
            auth_url=self.config.hercules_auth_url,
            client_id=self.config.hercules_client_id,
            client_secret=self.config.hercules_client_secret,
        )
        self.realtime = RealtimeTransportAdapter(enabled=self.config.enable_mock_realtime)
        self.wallet = WalletProviderAdapter(enabled=self.config.enable_mock_wallet)


container = Container()
