import streamlit as st

NII_OMS_CONSULTATION = (
    "Запишитесь на приём или направьте пациента на консультацию "
    "в НИИ ОМС ул. Репина д. 1 г. Екатеринбург"
)


def render_result(
    *,
    is_positive: bool,
    title: str,
    positive_msg: str,
    negative_msg: str,
) -> None:
    """Render outcome banner and optional NII OMS consultation text."""
    st.subheader(title)
    if is_positive:
        st.success(positive_msg)
    else:
        st.error(negative_msg)
        st.warning(NII_OMS_CONSULTATION)
