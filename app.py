import streamlit as st
import pandas as pd

# =====================================================
# CẤU HÌNH
# =====================================================
st.set_page_config(
    page_title="Smart Loan",
    page_icon="🏦",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
}

.sub-title {
    text-align: center;
    color: #666;
    font-size: 20px;
    margin-bottom: 25px;
}

.chat-box {
    padding: 15px;
    border-radius: 12px;
    background-color: #f5f7fa;
    border: 1px solid #ddd;
    margin-top: 10px;
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# HÀM ĐỊNH DẠNG TIỀN
# =====================================================
def money(value):
    return f"{value:,.0f} VNĐ"


# =====================================================
# TÍNH GỐC ĐỀU - LÃI GIẢM DẦN
# =====================================================
def calculate_equal_principal(loan, months, annual_rate):

    monthly_rate = annual_rate / 100 / 12
    principal_month = loan / months

    remaining = loan
    data = []

    for month in range(1, months + 1):

        interest = remaining * monthly_rate

        if month == months:
            principal = remaining
        else:
            principal = principal_month

        payment = principal + interest

        ending_balance = remaining - principal

        data.append([
            month,
            remaining,
            principal,
            interest,
            payment,
            max(ending_balance, 0)
        ])

        remaining = max(ending_balance, 0)

    return pd.DataFrame(
        data,
        columns=[
            "Tháng",
            "Dư nợ đầu kỳ",
            "Tiền gốc",
            "Tiền lãi",
            "Tổng trả",
            "Dư nợ cuối kỳ"
        ]
    )


# =====================================================
# TÍNH TRẢ GÓP ĐỀU
# =====================================================
def calculate_annuity(loan, months, annual_rate):

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        payment = loan / months
    else:
        payment = (
            loan
            * monthly_rate
            * (1 + monthly_rate) ** months
            / ((1 + monthly_rate) ** months - 1)
        )

    remaining = loan
    data = []

    for month in range(1, months + 1):

        interest = remaining * monthly_rate

        if month == months:
            principal = remaining
            actual_payment = principal + interest
        else:
            principal = payment - interest
            actual_payment = payment

        ending_balance = remaining - principal

        data.append([
            month,
            remaining,
            principal,
            interest,
            actual_payment,
            max(ending_balance, 0)
        ])

        remaining = max(ending_balance, 0)

    return pd.DataFrame(
        data,
        columns=[
            "Tháng",
            "Dư nợ đầu kỳ",
            "Tiền gốc",
            "Tiền lãi",
            "Tổng trả",
            "Dư nợ cuối kỳ"
        ]
    )


# =====================================================
# CHATBOT
# =====================================================
def chatbot_answer(question, loan, months, annual_rate, df):

    q = question.lower()

    total_interest = df["Tiền lãi"].sum()
    total_payment = df["Tổng trả"].sum()
    first_interest = df.iloc[0]["Tiền lãi"]
    first_payment = df.iloc[0]["Tổng trả"]

    # Tiền lãi
    if "lãi tháng đầu" in q or "lãi đầu" in q:
        return (
            f"💰 Tiền lãi tháng đầu khoảng "
            f"*{money(first_interest)}*."
        )

    # Tổng lãi
    if "tổng lãi" in q or "tổng tiền lãi" in q:
        return (
            f"📈 Tổng tiền lãi của khoản vay khoảng "
            f"*{money(total_interest)}*."
        )

    # Tổng trả
    if (
        "tổng phải trả" in q
        or "tổng trả" in q
        or "phải trả bao nhiêu" in q
    ):
        return (
            f"💵 Tổng số tiền phải trả khoảng "
            f"*{money(total_payment)}*."
        )

    # Thanh toán tháng đầu
    if (
        "tháng đầu" in q
        or "trả tháng đầu" in q
        or "thanh toán tháng đầu" in q
    ):
        return (
            f"📅 Tháng đầu tiên bạn cần thanh toán khoảng "
            f"*{money(first_payment)}*."
        )

    # Lãi suất
    if "lãi suất" in q:
        return (
            f"📊 Lãi suất bạn đang nhập là "
            f"*{annual_rate:.2f}%/năm*."
        )

    # Số tiền vay
    if "số tiền vay" in q or "vay bao nhiêu" in q:
        return (
            f"💰 Khoản vay hiện tại là *{money(loan)}*."
        )

    # Thời hạn
    if "thời hạn" in q or "bao lâu" in q:
        return (
            f"📅 Thời hạn khoản vay là *{months} tháng*."
        )

    # Tư vấn phương thức
    if "phương thức" in q or "gốc đều" in q:

        return """
🏦 *Tư vấn phương thức trả nợ:*

- *Gốc đều - lãi giảm dần:* số tiền trả mỗi tháng giảm dần, tổng tiền lãi thường thấp hơn.
- *Trả góp đều:* số tiền thanh toán hàng tháng gần như cố định, dễ lập kế hoạch tài chính.

Nếu ưu tiên *giảm tổng tiền lãi*, có thể cân nhắc phương thức gốc đều.
"""

    # Công thức
    if "công thức" in q or "tính như thế nào" in q:

        return """
🧮 *Cách tính cơ bản:*

Tiền lãi tháng = Dư nợ × Lãi suất tháng.

Lãi suất tháng = Lãi suất năm ÷ 12.

Tiền phải trả = Tiền gốc + Tiền lãi.
"""

    # Chào hỏi
    if (
        "xin chào" in q
        or "hello" in q
        or "hi" in q
        or "chào" in q
    ):
        return """
👋 Xin chào! Mình là *Smart Loan Assistant*.

Bạn có thể hỏi mình:
- Tiền lãi tháng đầu bao nhiêu?
- Tổng tiền lãi?
- Tổng phải trả?
- Lãi suất hiện tại?
- Thời hạn vay?
- Nên chọn phương thức trả nợ nào?
"""

    return """
🤖 Mình chưa hiểu câu hỏi này.

Bạn có thể thử hỏi:

*“Tiền lãi tháng đầu bao nhiêu?”*

*“Tổng tiền lãi là bao nhiêu?”*

*“Tổng phải trả bao nhiêu?”*

*“Lãi suất hiện tại là bao nhiêu?”*

*“Nên chọn phương thức trả nợ nào?”*
"""


# =====================================================
# TIÊU ĐỀ
# =====================================================
st.markdown(
    '<div class="main-title">🏦 SMART LOAN</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'TÍNH TOÁN KHOẢN VAY NGÂN HÀNG'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "💡 Nhập số tiền vay, thời hạn và lãi suất để tính "
    "gốc – lãi – lịch trả nợ."
)


# =====================================================
# THÔNG TIN KHOẢN VAY
# =====================================================
st.header("📋 THÔNG TIN KHOẢN VAY")

col1, col2, col3 = st.columns(3)

with col1:

    loan = st.number_input(
        "💰 Số tiền vay (VNĐ)",
        min_value=1_000_000,
        value=100_000_000,
        step=5_000_000
    )

with col2:

    months = st.number_input(
        "📅 Thời hạn vay (tháng)",
        min_value=1,
        max_value=360,
        value=12,
        step=1
    )

with col3:

    # NGƯỜI DÙNG TỰ NHẬP LÃI SUẤT
    annual_rate = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.1,
        help="Bạn có thể nhập bất kỳ mức lãi suất nào, ví dụ 7%, 8.5%, 10.2%..."
    )


# =====================================================
# LÃI SUẤT NHANH
# =====================================================
st.write("⚡ *Chọn nhanh lãi suất:*")

rate1, rate2, rate3, rate4, rate5 = st.columns(5)

if rate1.button("6%"):
    annual_rate = 6.0

if rate2.button("7%"):
    annual_rate = 7.0

if rate3.button("8%"):
    annual_rate = 8.0

if rate4.button("9%"):
    annual_rate = 9.0

if rate5.button("10%"):
    annual_rate = 10.0


col4, col5, col6 = st.columns(3)

with col4:

    purpose = st.selectbox(
        "🎯 Mục đích vay",
        [
            "Vay tiêu dùng",
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay kinh doanh",
            "Vay học tập",
            "Vay sửa chữa nhà"
        ]
    )

with col5:

    product = st.selectbox(
        "🏦 Sản phẩm vay",
        [
            "Vay tín chấp",
            "Vay thế chấp",
            "Vay tiêu dùng cá nhân",
            "Vay mua nhà",
            "Vay mua ô tô",
            "Vay kinh doanh"
        ]
    )

with col6:

    method = st.selectbox(
        "🔄 Phương thức trả nợ",
        [
            "Gốc đều - lãi giảm dần",
            "Trả góp đều hàng tháng"
        ]
    )


st.divider()


# =====================================================
# TÍNH TOÁN
# =====================================================
if st.button(
    "🧮 TÍNH KHOẢN VAY",
    use_container_width=True,
    type="primary"
):

    if method == "Gốc đều - lãi giảm dần":

        df = calculate_equal_principal(
            loan,
            months,
            annual_rate
        )

    else:

        df = calculate_annuity(
            loan,
            months,
            annual_rate
        )


    # =================================================
    # KẾT QUẢ
    # =================================================

    first_principal = df.iloc[0]["Tiền gốc"]
    first_interest = df.iloc[0]["Tiền lãi"]
    first_payment = df.iloc[0]["Tổng trả"]

    total_interest = df["Tiền lãi"].sum()
    total_payment = df["Tổng trả"].sum()


    st.success("✅ Đã tính toán khoản vay thành công!")

    st.header("📊 KẾT QUẢ")

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Gốc tháng đầu",
        money(first_principal)
    )

    r2.metric(
        "Lãi tháng đầu",
        money(first_interest)
    )

    r3.metric(
        "Thanh toán tháng đầu",
        money(first_payment)
    )

    r4.metric(
        "Tổng tiền lãi",
        money(total_interest)
    )


    # =================================================
    # THÔNG TIN
    # =================================================

    st.markdown(
        f"""
        <div class="chat-box">

        <h3>🏦 THÔNG TIN KHOẢN VAY</h3>

        💰 Số tiền vay:
        <b>{money(loan)}</b>

        <br><br>

        📅 Thời hạn:
        <b>{months} tháng</b>

        <br><br>

        📈 Lãi suất:
        <b>{annual_rate:.2f}%/năm</b>

        <br><br>

        🎯 Mục đích:
        <b>{purpose}</b>

        <br><br>

        🏦 Sản phẩm:
        <b>{product}</b>

        <br><br>

        🔄 Phương thức:
        <b>{method}</b>

        <br><br>

        💵 Tổng tiền phải trả:
        <b>{money(total_payment)}</b>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =================================================
    # LỊCH TRẢ NỢ
    # =================================================

    st.header("📅 LỊCH TRẢ NỢ")

    display_df = df.copy()

    money_columns = [
        "Dư nợ đầu kỳ",
        "Tiền gốc",
        "Tiền lãi",
        "Tổng trả",
        "Dư nợ cuối kỳ"
    ]

    for column in money_columns:

        display_df[column] = display_df[column].apply(money)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # =================================================
    # BIỂU ĐỒ
    # =================================================

    st.header("📈 BIỂU ĐỒ GỐC VÀ LÃI")

    chart_data = df.set_index("Tháng")[
        ["Tiền gốc", "Tiền lãi"]
    ]

    st.bar_chart(chart_data)


    st.header("📉 DƯ NỢ CÒN LẠI")

    balance_data = df.set_index("Tháng")[
        ["Dư nợ cuối kỳ"]
    ]

    st.line_chart(balance_data)


    # =================================================
    # DOWNLOAD
    # =================================================

    st.header("📥 XUẤT LỊCH TRẢ NỢ")

    csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "⬇️ TẢI LỊCH TRẢ NỢ (.CSV)",
        data=csv,
        file_name="lich_tra_no_smart_loan.csv",
        mime="text/csv",
        use_container_width=True
    )


    # =================================================
    # CHATBOT
    # =================================================

    st.divider()

    st.header("🤖 SMART LOAN ASSISTANT")

    st.write(
        "Bạn có thể hỏi chatbot về khoản vay vừa tính."
    )

    question = st.chat_input(
        "💬 Nhập câu hỏi về khoản vay..."
    )

    if question:

        st.chat_message("user").write(question)

        answer = chatbot_answer(
            question,
            loan,
            months,
            annual_rate,
            df
        )

        st.chat_message("assistant").write(answer)


    # =================================================
    # NHẬN XÉT
    # =================================================

    st.header("💡 NHẬN XÉT")

    interest_ratio = total_interest / loan

    if interest_ratio <= 0.08:

        st.success(
            "Khoản tiền lãi tương đối thấp so với số tiền vay."
        )

    elif interest_ratio <= 0.20:

        st.warning(
            "Khoản tiền lãi ở mức trung bình. "
            "Nên cân nhắc khả năng trả nợ hàng tháng."
        )

    else:

        st.error(
            "Tổng tiền lãi khá cao. "
            "Có thể cân nhắc giảm số tiền vay hoặc thời hạn vay."
        )


else:

    # =================================================
    # MÀN HÌNH CHÍNH
    # =================================================

    st.header("👋 CHÀO MỪNG ĐẾN VỚI SMART LOAN")

    st.write(
        "Nhập thông tin khoản vay và nhấn "
        *🧮 TÍNH KHOẢN VAY** để bắt đầu."
    )

    st.markdown("""
    ### ✨ CHỨC NĂNG

    💰 Tính tiền gốc hàng tháng

    📈 Tính tiền lãi hàng tháng

    📅 Lập lịch trả nợ

    📊 Biểu đồ gốc – lãi

    📉 Theo dõi dư nợ

    🎯 Chọn mục đích vay

    🏦 Chọn sản phẩm vay

    🤖 Chatbot tư vấn khoản vay

    📥 Xuất lịch trả nợ
    """)


# =====================================================
# FOOTER
# =====================================================
st.markdown(
    '<div class="footer">'
    '🏦 SMART LOAN • Ứng dụng tính toán khoản vay ngân hàng'
    '</div>',
    unsafe_allow_html=True
)
