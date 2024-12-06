class PaymentError(Exception):
    """کلاس پایه برای خطاهای پرداخت"""
    pass

class PaymentGatewayError(PaymentError):
    """خطای درگاه پرداخت"""
    def __init__(self, message, gateway_code=None):
        self.gateway_code = gateway_code
        super().__init__(message)

class PaymentVerificationError(PaymentError):
    """خطای تایید پرداخت"""
    def __init__(self, message, tracking_code=None):
        self.tracking_code = tracking_code
        super().__init__(message)

class InvalidPaymentAmount(PaymentError):
    """مبلغ پرداخت نامعتبر"""
    def __init__(self, amount, min_amount=None, max_amount=None):
        self.amount = amount
        self.min_amount = min_amount
        self.max_amount = max_amount
        message = "مبلغ پرداخت نامعتبر است"
        if min_amount and max_amount:
            message = f"مبلغ پرداخت باید بین {min_amount:,} و {max_amount:,} تومان باشد"
        super().__init__(message)

class PaymentExpiredError(PaymentError):
    """منقضی شدن پرداخت"""
    def __init__(self, payment_id=None, expiry_time=None):
        self.payment_id = payment_id
        self.expiry_time = expiry_time
        message = "مهلت پرداخت به پایان رسیده است"
        if expiry_time:
            message = f"مهلت پرداخت در {expiry_time} به پایان رسیده است"
        super().__init__(message)

class DuplicatePaymentError(PaymentError):
    """پرداخت تکراری"""
    def __init__(self, booking_id=None):
        self.booking_id = booking_id
        message = "این رزرو قبلاً پرداخت شده است"
        super().__init__(message)

class InsufficientFundsError(PaymentError):
    """موجودی ناکافی"""
    def __init__(self, required_amount, available_amount=None):
        self.required_amount = required_amount
        self.available_amount = available_amount
        message = f"موجودی کافی نیست. مبلغ مورد نیاز: {required_amount:,} تومان"
        if available_amount:
            message += f" (موجودی فعلی: {available_amount:,} تومان)"
        super().__init__(message)

class PaymentCanceledError(PaymentError):
    """لغو پرداخت توسط کاربر"""
    def __init__(self, tracking_code=None):
        self.tracking_code = tracking_code
        message = "پرداخت توسط کاربر لغو شد"
        if tracking_code:
            message = f"پرداخت با کد پیگیری {tracking_code} توسط کاربر لغو شد"
        super().__init__(message)

class InvalidGatewayError(PaymentError):
    """درگاه پرداخت نامعتبر"""
    def __init__(self, gateway=None):
        self.gateway = gateway
        message = "درگاه پرداخت نامعتبر است"
        if gateway:
            message = f"درگاه پرداخت {gateway} معتبر نیست"
        super().__init__(message)

class RefundError(PaymentError):
    """خطای استرداد وجه"""
    def __init__(self, message, payment_id=None):
        self.payment_id = payment_id
        super().__init__(message)

class InvalidBankAccountError(PaymentError):
    """شماره حساب نامعتبر"""
    def __init__(self, account_number=None):
        self.account_number = account_number
        message = "شماره حساب نامعتبر است"
        if account_number:
            message = f"شماره حساب {account_number} نامعتبر است"
        super().__init__(message)