from django.utils.translation import gettext_lazy as _


class MarketChoices(str):
    Mercadona = "mercadona"
    Carrefour = "carrefour"
    Lidl = "lidl"
    Alcampo = "alcampo"
    Other = "other"

    values = (
        (Mercadona, _("Mercadona")),
        (Carrefour, _("Carrefour")),
        (Lidl, _("Lidl")),
        (Alcampo, _("Alcampo")),
        (Other, _("Otro")),
    )

    @classmethod
    def choices(cls):
        return MarketChoices.values


class StockChoices(str):
    Yes = "yes"
    No = "no"
    Buy = "buy"

    values = (
        (Yes, _("SI")),
        (No, _("NO")),
        (Buy, _("Comprar")),
    )

    @classmethod
    def choices(cls):
        return StockChoices.values
