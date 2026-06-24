from voice_helper.schema import FieldSpec, FieldType

WI_FIELDS: list[FieldSpec] = [
    FieldSpec(
        key="x1",
        label="Двустороннее поражение почек (X1)",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "Двустороннее поражение почек. "
            "Скажите: да или нет."
        ),
    ),
    FieldSpec(
        key="x2",
        label="Мужской пол (X2)",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "Мужской пол плода. "
            "Скажите: да или нет."
        ),
    ),
    FieldSpec(
        key="x3",
        label="Продольный размер почки, мм (X3)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Продольный размер почки в миллиметрах. "
            "Скажите число."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="x4",
        label="Толщина паренхимы, мм (X4)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Толщина паренхимы в миллиметрах. "
            "Скажите число."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="x5",
        label="Индекс васкуляризации VI (X5)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Индекс васкуляризации VI. "
            "Скажите число."
        ),
    ),
    FieldSpec(
        key="x6",
        label="Индекс потока FI (X6)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Индекс потока FI. "
            "Скажите число."
        ),
    ),
]

DI_FIELDS: list[FieldSpec] = [
    FieldSpec(
        key="y1",
        label="Продольный размер почки, мм (Y1)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Продольный размер почки в миллиметрах. "
            "Скажите число."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="y2",
        label="Толщина паренхимы, мм (Y2)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Толщина паренхимы в миллиметрах. "
            "Скажите число."
        ),
        min_value=0.0,
    ),
    FieldSpec(
        key="y3",
        label="Индекс васкуляризации VI (Y3)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Индекс васкуляризации VI. "
            "Скажите число."
        ),
    ),
    FieldSpec(
        key="y4",
        label="Индекс потока FI (Y4)",
        field_type=FieldType.NUMBER,
        tts_prompt=(
            "Индекс потока FI. "
            "Скажите число."
        ),
    ),
    FieldSpec(
        key="y5",
        label="Почка-киста (Y5)",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "Почка-киста. "
            "Скажите: да или нет."
        ),
    ),
    FieldSpec(
        key="y6",
        label="Кистозная дисплазия (Y6)",
        field_type=FieldType.BOOLEAN,
        tts_prompt=(
            "Кистозная дисплазия. "
            "Скажите: да или нет."
        ),
    ),
]
