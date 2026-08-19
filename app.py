import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Financial Advisor & Expense Manager",
    page_icon="💰",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("💰 Financial Advisor & Expense Manager")

st.write(
    "Upload a payment screenshot to automatically extract "
    "expense information."
)


# =========================================================
# EXPENSE CATEGORIZATION
# =========================================================

def categorize_expense(text):

    text = text.lower()

    categories = {

        "🍔 Food": [
            "swiggy",
            "zomato",
            "restaurant",
            "food",
            "dominos",
            "pizza",
            "burger",
            "biryani",
            "kfc",
            "mcdonald",
            "hotel",
            "eat"
        ],

        "🚗 Transport": [
            "uber",
            "ola",
            "rapido",
            "petrol",
            "diesel",
            "fuel",
            "parking",
            "toll",
            "metro",
            "bus",
            "transport"
        ],

        "🛍️ Shopping": [
            "amazon",
            "flipkart",
            "myntra",
            "shopping",
            "mall",
            "store",
            "mart",
            "retail"
        ],

        "🎬 Entertainment": [
            "netflix",
            "spotify",
            "prime video",
            "hotstar",
            "movie",
            "cinema",
            "bookmyshow",
            "game"
        ],

        "💡 Bills & Utilities": [
            "electricity",
            "water bill",
            "mobile recharge",
            "recharge",
            "internet",
            "broadband",
            "airtel",
            "jio",
            "vi",
            "bill payment"
        ],

        "🏥 Health": [
            "hospital",
            "pharmacy",
            "medical",
            "medicine",
            "doctor",
            "apollo"
        ],

        "📚 Education": [
            "college",
            "school",
            "course",
            "udemy",
            "coursera",
            "education",
            "training",
            "books"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in text:
                return category

    return "📦 Other"


# =========================================================
# AMOUNT EXTRACTION
# =========================================================

def extract_amount(text):

    patterns = [

        # ₹450
        r'₹\s*([\d,]+(?:\.\d{1,2})?)',

        # Rs 450
        r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',

        # INR 450
        r'INR\s*([\d,]+(?:\.\d{1,2})?)',

        # 450.00
        r'(?<!\d)([\d,]+\.\d{2})(?!\d)'
    ]

    amounts = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for value in matches:

            try:

                amount = float(
                    value.replace(",", "")
                )

                if 0 < amount < 1000000:

                    amounts.append(amount)

            except ValueError:

                continue

    if amounts:

        return max(amounts)

    return None


# =========================================================
# MERCHANT EXTRACTION
# =========================================================

def extract_merchant(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    keywords = [

        "paid to",
        "sent to",
        "payment to",
        "paid",
        "receiver",
        "recipient",
        "merchant"
    ]

    for line in lines:

        lower_line = line.lower()

        for keyword in keywords:

            if keyword in lower_line:

                merchant = re.sub(
                    rf".*?{re.escape(keyword)}\s*:?\s*",
                    "",
                    line,
                    flags=re.IGNORECASE
                )

                if merchant.strip():

                    return merchant.strip()

    return "Unknown"


# =========================================================
# OCR PREPROCESSING
# =========================================================

def preprocess_image(image):

    # Convert to grayscale
    gray = image.convert("L")

    # Increase image size
    width, height = gray.size

    gray = gray.resize(
        (width * 2, height * 2)
    )

    # Improve contrast
    enhancer = ImageEnhance.Contrast(gray)

    gray = enhancer.enhance(2)

    # Sharpen image
    gray = gray.filter(
        ImageFilter.SHARPEN
    )

    return gray


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📊 Menu")

menu = st.sidebar.radio(

    "Select an option:",

    [
        "🏠 Dashboard",
        "📸 Upload Expense",
        "💳 Expenses",
        "📈 Analytics",
        "🤖 Financial Advisor"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if menu == "🏠 Dashboard":

    st.header("🏠 Financial Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Expenses",
            "₹0"
        )

    with col2:

        st.metric(
            "This Month",
            "₹0"
        )

    with col3:

        st.metric(
            "Budget Remaining",
            "₹0"
        )

    st.info(
        "Upload a payment screenshot to start "
        "tracking your expenses."
    )


# =========================================================
# UPLOAD EXPENSE
# =========================================================

elif menu == "📸 Upload Expense":

    st.header("📸 Upload Payment Screenshot")

    uploaded_file = st.file_uploader(

        "Choose a payment screenshot",

        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file is not None:

        # -------------------------------------------------
        # OPEN IMAGE
        # -------------------------------------------------

        image = Image.open(
            uploaded_file
        )

        st.success(
            "Screenshot uploaded successfully!"
        )

        st.image(
            image,
            caption="Uploaded Payment Screenshot",
            width=500
        )


        # -------------------------------------------------
        # PREPROCESS IMAGE
        # -------------------------------------------------

        st.subheader(
            "🛠️ Preparing Image..."
        )

        processed_image = preprocess_image(
            image
        )


        # Optional: show processed image

        with st.expander(
            "👁️ View Processed Image"
        ):

            st.image(
                processed_image,
                caption="Processed Image",
                width=500
            )


        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        st.subheader(
            "🔍 Extracting Text..."
        )

        try:

            extracted_text = pytesseract.image_to_string(

                processed_image,

                config="--psm 6"
            )


            # -------------------------------------------------
            # CHECK OCR RESULT
            # -------------------------------------------------

            if extracted_text.strip():

                st.success(
                    "Text extracted successfully!"
                )


                # -------------------------------------------------
                # RAW OCR OUTPUT
                # -------------------------------------------------

                with st.expander(
                    "🔎 View Raw OCR Output"
                ):

                    st.code(
                        extracted_text
                    )


                # -------------------------------------------------
                # EXTRACT EXPENSE INFORMATION
                # -------------------------------------------------

                amount = extract_amount(
                    extracted_text
                )

                merchant = extract_merchant(
                    extracted_text
                )

                category = categorize_expense(
                    extracted_text
                )


                # -------------------------------------------------
                # DISPLAY RESULTS
                # -------------------------------------------------

                st.subheader(
                    "💰 Extracted Expense Details"
                )

                col1, col2, col3 = st.columns(3)


                # Amount

                with col1:

                    if amount is not None:

                        st.metric(
                            "💰 Amount",
                            f"₹{amount:,.2f}"
                        )

                    else:

                        st.metric(
                            "💰 Amount",
                            "Not detected"
                        )


                # Merchant

                with col2:

                    st.metric(
                        "🏪 Merchant",
                        merchant
                    )


                # Category

                with col3:

                    st.metric(
                        "🏷️ Category",
                        category
                    )


                # -------------------------------------------------
                # RESULT MESSAGE
                # -------------------------------------------------

                if amount is not None:

                    st.success(
                        f"✅ Expense detected: "
                        f"₹{amount:,.2f}"
                    )

                else:

                    st.warning(
                        "⚠️ Amount could not be detected."
                    )


                if merchant != "Unknown":

                    st.success(
                        f"🏪 Merchant detected: "
                        f"{merchant}"
                    )

                else:

                    st.warning(
                        "⚠️ Merchant could not be detected."
                    )


                st.info(
                    f"🏷️ Expense Category: **{category}**"
                )


            else:

                st.warning(

                    "⚠️ No text could be detected. "
                    "Please upload a clearer payment screenshot."
                )


        except Exception as e:

            st.error(
                "❌ OCR processing failed."
            )

            st.exception(e)


# =========================================================
# EXPENSES
# =========================================================

elif menu == "💳 Expenses":

    st.header(
        "💳 Expense Manager"
    )

    st.info(
        "Extracted expenses will appear here "
        "after database storage is implemented."
    )


# =========================================================
# ANALYTICS
# =========================================================

elif menu == "📈 Analytics":

    st.header(
        "📈 Spending Analytics"
    )

    st.info(
        "Spending charts will be added "
        "in the next stage."
    )


# =========================================================
# FINANCIAL ADVISOR
# =========================================================

elif menu == "🤖 Financial Advisor":

    st.header(
        "🤖 AI Financial Advisor"
    )

    question = st.text_area(

        "Ask your financial question:",

        placeholder=(
            "Example: How can I reduce "
            "my monthly expenses?"
        )
    )

    if st.button(
        "Get Financial Advice"
    ):

        if question.strip():

            st.info(
                "AI financial advice will be "
                "connected in a later stage."
            )

        else:

            st.warning(
                "Please enter a financial question."
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Financial Advisor & Expense Manager AI Agent | Track A"
)