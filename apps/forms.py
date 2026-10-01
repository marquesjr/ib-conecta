from django import forms


class FormLabelsMixin:
    """Rótulos sem ":" e com "(opcional)" nos campos não obrigatórios.

    Caixas de seleção (consentimento, preferências) e os campos listados em
    ``OPTIONAL_MARK_EXEMPT`` ficam como estão.
    """

    OPTIONAL_MARK_EXEMPT: tuple = ()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (
                field.required
                or isinstance(field.widget, forms.CheckboxInput)
                or name in self.OPTIONAL_MARK_EXEMPT
                or not field.label
                or "(opcional)" in field.label
            ):
                continue
            field.label = f"{field.label} (opcional)"
