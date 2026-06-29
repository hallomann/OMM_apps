from voice_helper.schema import FieldSpec, FieldType

SFFT_FIELDS: list[FieldSpec] = [
    FieldSpec(
        key="ph",
        label="ПХ — предлежание хориона",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "ПХ — предлежание хориона. "
            "Скажите значение: есть или нет."
        ),
    ),
    FieldSpec(
        key="ktr1",
        label="КТР1 (мм)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "КТР первого плода в миллиметрах. "
            "Скажите число. Для лучшего распознавания можно произнести цифры по отдельности, например четыре пять."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="ktr2",
        label="КТР2 (мм)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "КТР второго плода в миллиметрах. "
            "Скажите число. Для лучшего распознавания можно произнести цифры по отдельности, например четыре пять."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="pi2",
        label="ПИ 2-го плода более 95%",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "ПИ второго плода более девяноста пяти процентов. "
            "Скажите: да или нет."
        ),
    ),
    FieldSpec(
        key="tvp_gt3",
        label="ТВП 1 или 2 плода > 3 мм",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "ТВП первого или второго плода больше трёх миллиметров. "
            "Скажите: да или нет."
        ),
    ),
]
