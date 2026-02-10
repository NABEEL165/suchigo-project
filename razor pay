{% extends 'customer_dashboard.html' %}

{% block title %}Razorpay Checkout{% endblock %}

{% block content %}
<style>
.checkout-container {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: white;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
    text-align: center;
}

.checkout-header {
    margin-bottom: 2rem;
}

.checkout-header h1 {
    color: #2c3e50;
    margin-bottom: 0.5rem;
}

.checkout-header p {
    color: #6c757d;
}

.order-details {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: left;
}

.order-details h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 0.5rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #dee2e6;
}

.detail-row:last-child {
    border-bottom: none;
}

.detail-label {
    font-weight: 500;
}

.detail-value {
    font-weight: 600;
}

.payment-form {
    display: none;
}

.btn-pay {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    border: none;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 1rem 0;
}

.btn-pay:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,123,255,0.3);
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #007bff;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
    display: none;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
    .checkout-container {
        margin: 1rem;
        padding: 1rem;
    }
}
</style>

<div class="checkout-container">
    <div class="checkout-header">
        <h1>Secure Payment</h1>
        <p>You will be redirected to Razorpay to complete your payment</p>
    </div>

    <div class="order-details">
        <h3>Order Details</h3>
        <div class="detail-row">
            <span class="detail-label">Service:</span>
            <span class="detail-value">{{ waste_info.waste_type }} Collection</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Customer:</span>
            <span class="detail-value">{{ waste_info.full_name }}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Address:</span>
            <span class="detail-value">{{ waste_info.pickup_address }}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Number of Bags:</span>
            <span class="detail-value">{{ waste_info.number_of_bags }}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Amount:</span>
            <span class="detail-value">₹{{ payment.amount }}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Transaction ID:</span>
            <span class="detail-value">{{ payment.transaction_id }}</span>
        </div>
    </div>

    <div class="spinner" id="spinner"></div>

    <button class="btn-pay" id="rzp-button1">Pay ₹{{ payment.amount }}</button>

    <form class="payment-form" id="paymentForm" action="{% url 'payments:payment_success' payment.id %}" method="POST">
        {% csrf_token %}
    </form>
</div>

<script src="https://checkout.razorpay.com/v1/checkout.js"></script>
<script>
document.getElementById('rzp-button1').onclick = function(e){
    e.preventDefault();

    // Show spinner
    document.getElementById('spinner').style.display = 'block';

    var options = {
        "key": "{{ razorpay_key }}", // Enter the Key ID generated from the Dashboard
        "amount": "{{ total_amount_in_paise }}", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
        "currency": "INR",
        "name": "SuchiGo Waste Management",
        "description": "{{ waste_info.waste_type }} Collection Service",
        "image": "https://example.com/your_logo",
        "order_id": "{{ order_data.id }}", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
        "handler": function (response){
            // On successful payment, submit the form to mark payment as successful
            document.getElementById('paymentForm').submit();
        },
        "prefill": {
            "name": "{{ waste_info.full_name }}",
            "email": "{{ request.user.email }}",
            "contact": "{{ waste_info.secondary_number|default:request.user.contact_number }}"
        },
        "notes": {
            "address": "{{ waste_info.pickup_address }}"
        },
        "theme": {
            "color": "#007bff"
        }
    };

    var rzp1 = new Razorpay(options);
    rzp1.on('payment.failed', function (response){
        // Hide spinner
        document.getElementById('spinner').style.display = 'none';

        // Redirect to failure page
        window.location.href = "{% url 'payments:payment_failure' payment.id %}";
    });

    rzp1.open();
};
</script>
{% endblock %}
