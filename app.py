import streamlit as st
import pandas as pd

# =========================================================
# CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Smart Loan",
    page_icon="🏦",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-top: 10px;
}

.sub-title {
    text-align: center;
    color: #666666;
    font-size: 20px;
    margin-bottom: 25px;
}

.box {
    padding: 20px;
    border-radius: 15px;
    background-color: #f7f9fc;
    border: 1px solid #dddddd;
    margin: 15px 0;
}

.footer {
    text-align: center;
    color: #888888;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================
def money(value):
    return f"{value:,.0f} VNĐ"


# =========================================================
# PHƯƠNG THỨC 1:
# GỐC ĐỀU - LÃI GIẢM DẦN
# =========================================================
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


# =========================================================
# PHƯƠNG THỨC 2:
# TRẢ GÓP ĐỀU HÀNG THÁNG
# =========================================================
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


# =========================================================
# CHATBOT
# =========================================================
def chatbot_answer(question, loan, months, annual_rate, df):

    q = question.lower().strip()

    total_interest = df["Tiền lãi"].sum()
    total_payment = df["Tổng trả"].sum()

    first_interest = df.iloc[0]["Tiền lãi"]
    first_payment = df.iloc[0]["Tổng trả"]

    # -----------------------------------------
    # CHÀO HỎI
    # -----------------------------------------
    if (
        "xin chào" in q
        or "chào" in q
        or "hello" in q
        or "hi" in q
    ):
        return """
👋 Xin chào! Mình là *Smart Loan Assistant*.

Mình có thể giúp bạn xem nhanh thông tin khoản vay.

Bạn có thể hỏi:

• Tiền lãi tháng đầu bao nhiêu?
• Tổng tiền lãi là bao nhiêu?
• Tổng phải trả bao nhiêu?
• Lãi suất hiện tại là bao nhiêu?
• Thời hạn vay bao lâu?
• Số tiền vay bao nhiêu?
• Nên chọn phương thức trả nợ nào?
"""

    # -----------------------------------------
    # LÃI THÁNG ĐẦU
    # -----------------------------------------
    if (
        "lãi tháng đầu" in q
        or "lãi đầu" in q
        or "tiền lãi đầu" in q
    ):
        return (
            "💰 Tiền lãi tháng đầu là khoảng "
            + money(first_interest)
            + "."
        )

    # -----------------------------------------
    # TỔNG LÃI
    # -----------------------------------------
    if (
        "tổng lãi" in q
        or "tổng tiền lãi" in q
    ):
        return (
            "📈 Tổng tiền lãi của khoản vay là khoảng "
            + money(total_interest)
            + "."
        )

    # -----------------------------------------
    # TỔNG PHẢI TRẢ
    # -----------------------------------------
    if (
        "tổng phải trả" in q
        or "tổng tiền phải trả" in q
        or "tổng trả" in q
    ):
        return (
            "💵 Tổng số tiền phải trả là khoảng "
            + money(total_payment)
            + "."
        )

    # -----------------------------------------
    # THANH TOÁN THÁNG ĐẦU
    # -----------------------------------------
    if (
        "thanh toán tháng đầu" in q
        or "trả tháng đầu" in q
    ):
        return (
            "📅 Số tiền cần thanh toán tháng đầu là khoảng "
            + money(first_payment)
            + "."
        )

    # -----------------------------------------
    # LÃI SUẤT
    # -----------------------------------------
    if "lãi suất" in q:
        return (
            "📊 Lãi suất bạn đang sử dụng là "
            + f"{annual_rate:.2f}%/năm."
        )

    # -----------------------------------------
    # SỐ TIỀN VAY
    # -----------------------------------------
    if (
        "số tiền vay" in q
        or "khoản vay" in q
        or "vay bao nhiêu" in q
    ):
        return (
            "💰 Số tiền vay hiện tại là "
            + money(loan)
            + "."
        )

    # -----------------------------------------
    # THỜI HẠN
    # -----------------------------------------
    if (
        "thời hạn" in q
        or "bao lâu" in q
        or "mấy tháng" in q
    ):
        return (
            "📅 Thời hạn khoản vay là "
            + str(months)
            + " tháng."
        )

    # -----------------------------------------
    # PHƯƠNG THỨC
    # -----------------------------------------
    if (
        "phương thức" in q
        or "gốc đều" in q
        or "trả góp đều" in q
    ):
        return """
🏦 Có 2 phương thức trong ứng dụng:

*1. Gốc đều - lãi giảm dần*
- Tiền gốc mỗi tháng gần như bằng nhau.
- Tiền lãi giảm dần.
- Số tiền trả hàng tháng giảm dần.

*2. Trả góp đều*
- Số tiền thanh toán hàng tháng gần như cố định.
- Dễ lập kế hoạch chi tiêu.
"""

    # -----------------------------------------
    # CÔNG THỨC
    # -----------------------------------------
    if (
        "công thức" in q
        or "tính như thế nào" in q
    ):
        return """
🧮 Cách tính cơ bản:

Lãi suất tháng = Lãi suất năm / 12

Tiền lãi tháng =
Dư nợ đầu kỳ × Lãi suất tháng

Tiền thanh toán =
Tiền gốc + Tiền lãi
"""

    # -----------------------------------------
    # KHÔNG HIỂU
    # -----------------------------------------
    return """
🤖 Mình chưa hiểu câu hỏi.

Bạn thử hỏi:

• "Tiền lãi tháng đầu bao nhiêu?"
• "Tổng tiền lãi bao nhiêu?"
• "Tổng phải trả bao nhiêu?"
• "Lãi suất hiện tại là bao nhiêu?"
• "Số tiền vay bao nhiêu?"
• "Thời hạn vay bao lâu?"
• "Nên chọn phương thức nào?"
"""


# =========================================================
# TIÊU ĐỀ
# =========================================================
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
    "💡 Nhập số tiền vay, thời hạn và lãi suất để "
    "tính gốc, lãi và lịch trả nợ."
)


# =========================================================
# NHẬP THÔNG TIN
# =========================================================
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

    annual_rate = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=0.1
    )


# =========================================================
# CHỌN NHANH LÃI SUẤT
# =========================================================
st.write("⚡ *Lãi suất tham khảo nhanh:*")

c1, c2, c3, c4, c5 = st.columns(5)

if c1.button("6%"):
    annual_rate = 6.0

if c2.button("7%"):
    annual_rate = 7.0

if c3.button("8%"):
    annual_rate = 8.0

if c4.button("9%"):
    annual_rate = 9.0

if c5.button("10%"):
    annual_rate = 10.0


# =========================================================
# THÔNG TIN BỔ SUNG
# =========================================================
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


# =========================================================
# NÚT TÍNH TOÁN
# =========================================================
calculate_button = st.button(
    "🧮 TÍNH KHOẢN VAY",
    use_container_width=True,
    type="primary"
)


# =========================================================
# TÍNH TOÁN VÀ HIỂN THỊ
# =========================================================
if calculate_button:

    # -----------------------------------------
    # TÍNH
    # -----------------------------------------
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


    # -----------------------------------------
    # KẾT QUẢ
    # -----------------------------------------
    first_principal = df.iloc[0]["Tiền gốc"]
    first_interest = df.iloc[0]["Tiền lãi"]
    first_payment = df.iloc[0]["Tổng trả"]

    total_interest = df["Tiền lãi"].sum()
    total_payment = df["Tổng trả"].sum()


    st.success("✅ Đã tính toán khoản vay thành công!")


    # -----------------------------------------
    # 4 KẾT QUẢ CHÍNH
    # -----------------------------------------
    st.header("📊 KẾT QUẢ KHOẢN VAY")

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


    # -----------------------------------------
    # THÔNG TIN KHOẢN VAY
    # -----------------------------------------
    st.markdown(
        f"""
        <div class="box">

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


    # -----------------------------------------
    # LỊCH TRẢ NỢ
    # -----------------------------------------
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


    # -----------------------------------------
    # BIỂU ĐỒ
    # -----------------------------------------
    st.header("📈 BIỂU ĐỒ TIỀN GỐC VÀ TIỀN LÃI")

    chart_data = df.set_index("Tháng")[
        ["Tiền gốc", "Tiền lãi"]
    ]

    st.bar_chart(chart_data)


    # -----------------------------------------
    # BIỂU ĐỒ DƯ NỢ
    # -----------------------------------------
    st.header("📉 BIỂU ĐỒ DƯ NỢ CÒN LẠI")

    balance_data = df.set_index("Tháng")[
        ["Dư nợ cuối kỳ"]
    ]

    st.line_chart(balance_data)


    # -----------------------------------------
    # TẢI FILE
    # -----------------------------------------
    st.header("📥 XUẤT LỊCH TRẢ NỢ")

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="⬇️ TẢI LỊCH TRẢ NỢ (.CSV)",
        data=csv_data,
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
        "Hãy đặt câu hỏi về khoản vay của bạn:"
    )

    # Câu hỏi gợi ý
    q1, q2, q3 = st.columns(3)

    if q1.button("💬 Lãi tháng đầu?"):
        question = "Tiền lãi tháng đầu bao nhiêu?"

        st.chat_message("user").write(question)

        answer = chatbot_answer(
            question,
            loan,
            months,
            annual_rate,
            df
        )

        st.chat_message("assistant").write(answer)

    if q2.button("💬 Tổng tiền lãi?"):
        question = "Tổng tiền lãi bao nhiêu?"

        st.chat_message("user").write(question)

        answer = chatbot_answer(
            question,
            loan,
            months,
            annual_rate,
            df
        )

        st.chat_message("assistant").write(answer)

    if q3.button("💬 Tổng phải trả?"):
        question = "Tổng phải trả bao nhiêu?"

        st.chat_message("user").write(question)

        answer = chatbot_answer(
            question,
            loan,
            months,
            annual_rate,
            df
        )

        st.chat_message("assistant").write(answer)


    # Ô nhập chatbot
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


    # -----------------------------------------
    # NHẬN XÉT
    # -----------------------------------------
    st.header("💡 NHẬN XÉT")

    interest_ratio = total_interest / loan

    if interest_ratio <= 0.08:

        st.success(
            "Khoản tiền lãi tương đối thấp so với số tiền vay."
        )

    elif interest_ratio <= 0.20:

        st.warning(
            "Khoản tiền lãi ở mức trung bình. "
            "Bạn nên cân nhắc khả năng trả nợ hàng tháng."
        )

    else:

        st.error(
            "Tổng tiền lãi khá cao. "
            "Có thể cân nhắc giảm số tiền vay hoặc thời hạn vay."
        )


    st.caption(
        "⚠️ Ứng dụng phục vụ mục đích học tập và mô phỏng. "
        "Lãi suất thực tế có thể thay đổi tùy ngân hàng "
        "và hợp đồng tín dụng."
    )


# =========================================================
# MÀN HÌNH BAN ĐẦU
# =========================================================
else:

    st.header("👋 CHÀO MỪNG ĐẾN VỚI SMART LOAN")

    st.write(
        "Nhập thông tin khoản vay ở phía trên "
        "và nhấn nút*🧮 TÍNH KHOẢN VAY** để bắt đầu."
    )

    st.markdown("""
    ### ✨ CHỨC NĂNG CHÍNH

    💰 Tính tiền gốc hàng tháng

    📈 Tính tiền lãi hàng tháng

    📅 Lập lịch trả nợ

    📊 Biểu đồ gốc và lãi

    📉 Theo dõi dư nợ

    🎯 Chọn mục đích vay

    🏦 Chọn sản phẩm vay

    📈 Nhập lãi suất tùy ý

    🤖 Chatbot tư vấn khoản vay

    📥 Xuất lịch trả nợ
    """)


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    '<div class="footer">'
    '🏦 SMART LOAN • Ứng dụng tính toán khoản vay ngân hàng'
    '</div>',
    unsafe_allow_html=True
)
