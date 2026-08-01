from ai.trust.engine import engine


class TrustService:

    def analyze(self, image_result: dict):

        return engine.analyze(image_result)


trust_service = TrustService()