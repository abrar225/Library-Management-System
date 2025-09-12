
    document.addEventListener('DOMContentLoaded', function () {
        const form = document.querySelector('form[name="checkout"]');
        const phoneInput = document.getElementById('billing_phone');
        const zipInput = document.getElementById('billing_postcode');

        phoneInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
        });

        zipInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 6);
        });

        form.addEventListener('submit', function (e) {
            const phone = phoneInput.value.trim();
            const zip = zipInput.value.trim();

            const isPhoneValid = /^\d{10}$/.test(phone);
            const isZipValid = /^\d{6}$/.test(zip);

            if (!isPhoneValid || !isZipValid) {
                e.preventDefault();
                let errorMsg = '';
                if (!isPhoneValid) {
                    errorMsg += 'Phone number must be exactly 10 digits.\n';
                }
                if (!isZipValid) {
                    errorMsg += 'ZIP code must be exactly 6 digits.\n';
                }
                alert(errorMsg);
            }
        });
    });
